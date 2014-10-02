import logging

from nose.tools import eq_
import mock
import requests
import requests.adapters

from pylcp import api


class MockRequestAdapter(requests.adapters.BaseAdapter):
    """
    A requests Transport Adapter which logs the request instead of making acutal
    HTTP calls.

    Provides methods for asserting various properties of the request.
    """
    def __init__(self, *args, **kwargs):
        self.last_request = None
        self.last_request_kwargs = None

    def send(self, request, **kwargs):
        self.last_request = request
        self.last_request_kwargs = kwargs

        response = mock.MagicMock()
        response.request = request
        response.connection = self
        response.status_code = 200
        response.is_redirect = False
        response.reason = 'OK'
        response.headers = {
            'content-type': 'application/json',
            'location': request.url,
        }
        response.text = '{}'
        return response

    def close(self):
        pass  # no connection to close

    def assert_request_properties(self, **expected_properties):
        for property_name, expected_value in expected_properties.items():
            actual_value = getattr(self.last_request, property_name)
            message = '{} did not match. Expected: {}, actual: {}'.format(property_name, expected_value, actual_value)
            eq_(actual_value, expected_value, message)

    def assert_headers_present(self, expected_headers):
        for header_name, expected_value in expected_headers.items():
            actual_value = self.last_request.headers.get(header_name)
            message = 'Header {} did not match. Expected: {}, actual: {}'.format(
                header_name,
                expected_value,
                actual_value,
            )
            eq_(actual_value, expected_value, message)


class TestApiClient(object):

    def setup(self):
        api.logger.setLevel(logging.ERROR)
        self.client, self.test_adapter = self._get_client_and_adapter(base_url='http://BASE_URL')

    def _get_client_and_adapter(self, **client_kwargs):
        test_adapter = MockRequestAdapter()
        client = api.Client(**client_kwargs)
        client.mount('http://', test_adapter)
        client.mount('https://', test_adapter)
        return client, test_adapter

    def _assert_calls_requests_with_url(self, original_url, expected_url):
        self.client.request('METHOD', original_url)
        self.test_adapter.assert_request_properties(
            method='METHOD',
            url=expected_url,
        )

    def test_request_does_not_alter_absolute_urls(self):
        for absolute_url in ['http://www.points.com/', 'https://www.points.com/']:
            yield self._assert_calls_requests_with_url, absolute_url, absolute_url

    def test_request_adds_base_url_to_relative_urls(self):
        self._assert_calls_requests_with_url('some/relative/path', 'http://BASE_URL/some/relative/path')
        self._assert_calls_requests_with_url('/some/absolute/path', 'http://BASE_URL/some/absolute/path')

    def test_request_adds_base_url_with_trailing_slash_to_relative_urls(self):
        self.client.base_url = 'http://BASE_URL/'
        self._assert_calls_requests_with_url('some/relative/path', 'http://BASE_URL/some/relative/path')
        self._assert_calls_requests_with_url('/some/absolute/path', 'http://BASE_URL/some/absolute/path')

    def test_delete_issues_a_DELETE_request_with_none_headers(self):
        self.client.delete('/url')
        self.test_adapter.assert_request_properties(
            method='DELETE',
            url='http://BASE_URL/url',
        )

    def test_delete_issues_a_DELETE_request_with_custom_headers(self):
        headers = {'Header-Name': 'some header value'}
        self.client.delete('/url', headers=headers)
        self.test_adapter.assert_request_properties(
            method='DELETE',
            url='http://BASE_URL/url',
        )
        self.test_adapter.assert_headers_present(headers)

    def test_options_issues_an_OPTIONS_request_with_none_headers(self):
        self.client.options('/url')
        self.test_adapter.assert_request_properties(
            method='OPTIONS',
            url='http://BASE_URL/url',
        )

    def test_options_issues_an_OPTIONS_request_with_headers(self):
        headers = {'Header-Name': 'some header value'}
        self.client.options('/url', headers=headers)
        self.test_adapter.assert_request_properties(
            method='OPTIONS',
            url='http://BASE_URL/url',
        )
        self.test_adapter.assert_headers_present(headers)

    def test_put_issues_a_PUT_request_with_json_content_type(self):
        self.client.put('/url')
        self.test_adapter.assert_request_properties(
            method='PUT',
            url='http://BASE_URL/url',
        )
        self.test_adapter.assert_headers_present({'content-type': 'application/json'})

    def test_post_issues_a_POST_request_with_json_content_type(self):
        self.client.post('/url', data={})
        self.test_adapter.assert_request_properties(
            method='POST',
            url='http://BASE_URL/url',
        )
        self.test_adapter.assert_headers_present({'content-type': 'application/json'})

    @mock.patch('pylcp.api.generate_authorization_header_value', return_value='auth_value')
    def test_get_issues_a_GET_request_with_none_headers_and_none_params(self, auth_header_mock):
        client, test_adapter = self._get_client_and_adapter(
            base_url='http://BASE_URL',
            key_id='foobar',
        )

        client.get('/url')
        test_adapter.assert_request_properties(
            method='GET',
            url='http://BASE_URL/url',
        )
        test_adapter.assert_headers_present({'Authorization': 'auth_value'})

    def test_get_issues_a_GET_request_with_headers_and_params(self):
        headers = {'Header-Name': 'some header value'}
        params = {'paramName': 'param_value'}

        self.client.get('/url', headers=headers, params=params)
        self.test_adapter.assert_request_properties(
            method='GET',
            url='http://BASE_URL/url?paramName=param_value',
        )
        self.test_adapter.assert_headers_present(headers)

    @mock.patch('pylcp.api.generate_authorization_header_value', return_value='auth_value')
    def test_specifying_key_id_causes_Authorization_header_to_be_set(self, auth_header_mock):
        client, test_adapter = self._get_client_and_adapter(
            base_url='http://BASE_URL',
            key_id='foobar',
        )

        client.request('METHOD', '/url', headers={'Content-Type': 'application/json'})

        test_adapter.assert_request_properties(
            method='METHOD',
            url='http://BASE_URL/url',
        )
        test_adapter.assert_headers_present({'Authorization': 'auth_value'})

    def test_mask_sensitive_data_cleans_a_copy_of_data(self):
        data = {
            "amount": 20.11,
            "billingInfo": {
                "cardNumber": "4111111111111111",
                "cardType": "VISA",
                "email": "sonia.walia@points.com",
                "securityCode": "123",
                "state": "ON",
            },
        }
        masked_data = api.mask_sensitive_data(data)

        eq_(masked_data['billingInfo']['cardNumber'], "XXXXXXXXXXXX1111")
        eq_(masked_data['billingInfo']['securityCode'], "XXX")

        # assert that original source is unchanged
        eq_(data['billingInfo']['cardNumber'], "4111111111111111")
        eq_(data['billingInfo']['securityCode'], "123")

    @mock.patch('pylcp.api.mask_sensitive_data')
    def test_mask_data_is_during_post_request(self, mask_sensitive_data_mock):
        json_data = '{"test": "test"}'
        mask_sensitive_data_mock.return_value = json_data
        api.logger.setLevel(logging.DEBUG)
        self.client.post('/url', data=json_data)
        eq_(mask_sensitive_data_mock.call_args_list, [mock.call({'test': 'test'})])
