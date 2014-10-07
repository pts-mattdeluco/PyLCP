import collections
import json
import logging

from nose.tools import assert_in, assert_is_none, eq_
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
        response.text = request.body
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


class TestHeaderFormatting(object):
    def test_header_dict_formatted_as_string(self):
        headers = collections.OrderedDict()
        headers['header1'] = 'value1'
        headers['header2'] = 'value2'
        formatted_headers = 'header1: value1\nheader2: value2'
        eq_(formatted_headers, api.format_headers(headers))

    def test_empty_header_dict_formatted_as_empty_string(self):
        eq_('', api.format_headers({}))


class TestJsonPrettifying(object):
    def setup(self):
        self.indent_amount = 2

    def test_prettified_json_is_indented(self):
        eq_(
            '{{\n{0}"answer": 42\n}}'.format(' ' * self.indent_amount),
            api.prettify_alleged_json('{"answer": 42}')
        )

    def test_prettified_json_is_sorted(self):
        eq_(
            '{{\n{0}"x": 2, \n{0}"y": 1\n}}'.format(' ' * self.indent_amount),
            api.prettify_alleged_json('{"y": 1, "x": 2}')
        )

    def test_non_json_is_not_prettified(self):
        non_json = 'This is not JSON.'
        eq_(non_json, api.prettify_alleged_json(non_json))


class TestCreditCardDataMasking(object):
    def test_none_is_not_masked(self):
        assert_is_none(api.mask_credit_card_number(None))

    def test_all_but_last_four_digits_are_masked(self):
        card_number = '1234567890'
        masked_card_number = api.mask_credit_card_number(card_number)
        eq_(card_number[-4], masked_card_number[-4])
        eq_(len(card_number), len(masked_card_number))
        eq_('X' * (len(card_number) - 4), masked_card_number[:-4])


class TestSensitiveDataMasking(object):
    def setup(self):
        self.unmasked = {
            'billingInfo': {
                'cardNumber': '1234567890123456',
                'securityCode': '123',
            },
            'password': 'secret',
            'language': 'Python',
        }
        self.masked = api.mask_sensitive_data(self.unmasked)

    def test_non_data_is_not_masked(self):
        assert_is_none(api.mask_sensitive_data(None))
        assert_is_none(api.mask_sensitive_data(''))
        assert_is_none(api.mask_sensitive_data([]))
        assert_is_none(api.mask_sensitive_data({}))

    def test_non_json_data_is_not_masked(self):
        data = 'This is not JSON. cardNumber: 1234567890123456'
        eq_(data, api.mask_sensitive_data(data))

    def test_card_number_is_masked(self):
        eq_('XXXXXXXXXXXX3456', self.masked['billingInfo']['cardNumber'])

    def test_security_code_is_masked(self):
        eq_('XXX', self.masked['billingInfo']['securityCode'])

    def test_password_is_masked(self):
        eq_('XXX', self.masked['password'])

    def test_non_sensitive_data_is_not_masked(self):
        eq_(self.unmasked['language'], self.masked['language'])

    def test_json_in_a_string_is_masked(self):
        unmasked_string = '{"billingInfo": {}, "password": "secret"}'
        masked_string = '{"password": "XXX", "billingInfo": {}}'
        eq_(masked_string, api.mask_sensitive_data(unmasked_string))


class TestMaskingAndFormattingOfRequestBody(object):
    def setup(self):
        self.request = requests.Request()
        self.request.body = json.dumps({
            'billingInfo': {
                'cardNumber': '1234567890123456',
                'securityCode': '123',
            },
            'password': 'secret',
            'language': 'Python',
        })
        self.request.headers['content-type'] = 'application/json'

    def test_json_request_body_is_masked_and_formatted(self):
        result = api.get_masked_and_formatted_request_body(self.request)
        expected = {
            'billingInfo': {
                'cardNumber': 'XXXXXXXXXXXX3456',
                'securityCode': 'XXX',
            },
            'password': 'XXX',
            'language': 'Python',
        }
        eq_(json.dumps(expected, indent=2, sort_keys=True), result)

    def test_non_json_request_body_is_not_altered(self):
        request = requests.Request()
        request.body = 'This is not JSON'
        request.headers['content-type'] = 'text/plain'
        eq_(request.body, api.get_masked_and_formatted_request_body(request))

    def test_non_json_request_body_with_json_content_type_is_not_altered(self):
        self.request.body = 'This is not JSON'
        eq_(self.request.body, api.get_masked_and_formatted_request_body(self.request))


class TestApiClient(object):

    def setup(self):
        api.logger.setLevel(logging.DEBUG)
        self.client, self.test_adapter = self._get_client_and_adapter(base_url='http://BASE_URL')
        self.request_log_format_string = (
            '------------------------------------------------------------\n'
            '%(method)s %(url)s HTTP/1.1\n%'
            '(headers)s\n\n%(body)s')
        self.response_log_format_string = (
            '------------------------------------------------------------\n'
            'HTTP/1.1 %(status_code)d %(reason)s\n'
            '%(headers)s\n\n'
            '%(body)s')

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

    def assert_loggers_called(self, log_data):
        with mock.patch('pylcp.api.request_logger') as request_logger_mock:
            with mock.patch('pylcp.api.response_logger') as response_logger_mock:
                self.client.post('/url', data=json.dumps(log_data['body']))

                eq_(self.request_log_format_string, request_logger_mock.debug.call_args_list[0][0][0])
                log_format_dict = request_logger_mock.debug.call_args_list[0][0][1]
                eq_(log_data['url'], log_format_dict['url'])
                eq_(log_data['body'], json.loads(log_format_dict['body']))
                eq_(log_data['method'], log_format_dict['method'])
                assert_in(log_data['headers'], log_format_dict['headers'])

                eq_(self.response_log_format_string, response_logger_mock.debug.call_args_list[0][0][0])
                log_format_dict = response_logger_mock.debug.call_args_list[0][0][1]
                eq_(log_data['body'], json.loads(log_format_dict['body']))
                eq_(200, log_format_dict['status_code'])
                eq_('OK', log_format_dict['reason'])
                assert_in(log_data['headers'], log_format_dict['headers'])
                assert_in('location: ' + log_data['url'], log_format_dict['headers'])

    def test_request_does_not_alter_absolute_urls(self):
        for absolute_url in ['http://www.points.com/', 'https://www.points.com/']:
            yield self._assert_calls_requests_with_url, absolute_url, absolute_url

    def test_client_remembers_credentials(self):
        client = api.Client(mock.sentinel.BASE_URL, mock.sentinel.KEY_ID, mock.sentinel.SHARED_SECRET)
        eq_(mock.sentinel.BASE_URL, client.base_url)
        eq_(mock.sentinel.KEY_ID, client.key_id)
        eq_(mock.sentinel.SHARED_SECRET, client.shared_secret)

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

    def test_patch_issues_a_PATCH_request_with_json_content_type(self):
        self.client.patch('/url')
        self.test_adapter.assert_request_properties(
            method='PATCH',
            url='http://BASE_URL/url'
        )

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

    @mock.patch('pylcp.api.mask_sensitive_data')
    def test_mask_data_is_called_during_a_POST_request_with_json_content_type(
            self, mock_mask_sensitive_data):
        data = {"test": "test"}
        mock_mask_sensitive_data.return_value = data
        self.client.post('/url', data=json.dumps(data))
        eq_(mock_mask_sensitive_data.call_args_list, [
            mock.call(data)])

    def test_post_logs_with_json_data(self):
        log_data = {
            'url': 'http://BASE_URL/url',
            'headers': 'content-type: application/json',
            'body': {'answer': 42},
            'method': 'POST'
        }
        self.assert_loggers_called(log_data)

    def test_post_logs_with_non_json_data(self):
        log_data = {
            'url': 'http://BASE_URL/url',
            'headers': 'content-type: application/json',
            'body': 'This is not JSON',
            'method': 'POST'
        }
        self.assert_loggers_called(log_data)

    def test_no_request_or_response_logging_if_not_debug_level(self):
        with mock.patch('pylcp.api.request_logger') as request_logger_mock:
            request_logger_mock.isEnabledFor.return_value = False
            with mock.patch('pylcp.api.response_logger') as response_logger_mock:
                response_logger_mock.isEnabledFor.return_value = False
                self.client.post('/url', data='{}')
                eq_([], request_logger_mock.debug.call_args_list)
                eq_([], response_logger_mock.debug.call_args_list)
