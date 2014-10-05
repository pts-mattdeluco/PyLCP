import collections

from nose.tools import assert_is_none, eq_
import mock

from pylcp import api


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


class TestApiClient(object):
    def setup(self):
        self.client = api.Client('BASE_URL')
        self.request_log_format_string = (
            '------------------------------------------------------------\n'
            '%(method)s %(url)s HTTP/1.1\n%'
            '(headers)s\n\n%(body)s')
        self.response_log_format_string = (
            '------------------------------------------------------------\n'
            'HTTP/1.1 %(status_code)d %(reason)s\n'
            '%(headers)s\n\n'
            '%(body)s')

    def test_request_does_not_alter_absolute_urls(self):
        for absolute_url in [
                'http://www.points.com',
                'https://www.points.com']:
            yield self._assert_calls_requests_with_url, absolute_url, absolute_url

    def test_client_remembers_credentials(self):
        client = api.Client(mock.sentinel.BASE_URL, mock.sentinel.KEY_ID, mock.sentinel.SHARED_SECRET)
        eq_(mock.sentinel.BASE_URL, client.base_url)
        eq_(mock.sentinel.KEY_ID, client.key_id)
        eq_(mock.sentinel.SHARED_SECRET, client.shared_secret)

    def test_request_adds_base_url_to_relative_urls(self):
        self._assert_calls_requests_with_url('some/relative/path', 'BASE_URL/some/relative/path')
        self._assert_calls_requests_with_url('/some/absolute/path', 'BASE_URL/some/absolute/path')

    def test_request_adds_base_url_with_trailing_slash_to_relative_urls(self):
        self.client = api.Client('BASE_URL/')
        self._assert_calls_requests_with_url('some/relative/path', 'BASE_URL/some/relative/path')
        self._assert_calls_requests_with_url('/some/absolute/path', 'BASE_URL/some/absolute/path')

    @mock.patch('requests.request')
    def _assert_calls_requests_with_url(self, original_url, expected_url, request_mock):
        self.client.request('METHOD', original_url)
        eq_(request_mock.call_args_list, [
            mock.call('METHOD', expected_url, headers={})])

    @mock.patch('requests.request')
    def test_delete_issues_a_DELETE_request_with_none_headers(self, request_mock):
        self.client.delete('/url')
        eq_(request_mock.call_args_list, [
            mock.call('DELETE', 'BASE_URL/url', headers={})])

    @mock.patch('requests.request')
    def test_delete_issues_a_DELETE_request_with_headers(self, request_mock):
        self.client.delete('/url', headers={'Header-Name': 'some header value'})
        eq_(request_mock.call_args_list, [
            mock.call('DELETE', 'BASE_URL/url', headers={'Header-Name': 'some header value'})])

    @mock.patch('requests.request')
    def test_options_issues_an_OPTIONS_request_with_none_headers(self, request_mock):
        self.client.options('/url')
        eq_(request_mock.call_args_list, [
            mock.call('OPTIONS', 'BASE_URL/url', headers={})])

    @mock.patch('requests.request')
    def test_options_issues_an_OPTIONS_request_with_headers(self, request_mock):
        self.client.options('/url', headers={'Header-Name': 'some header value'})
        eq_(request_mock.call_args_list, [
            mock.call('OPTIONS', 'BASE_URL/url', headers={'Header-Name': 'some header value'})])

    @mock.patch('requests.request')
    def test_patch_issues_a_PATCH_request_with_json_content_type(self, request_mock):
        self.client.patch('/url')
        eq_(request_mock.call_args_list, [
            mock.call('PATCH', 'BASE_URL/url', headers={'Content-Type': 'application/json'})])

    @mock.patch('requests.request')
    def test_put_issues_a_PUT_request_with_json_content_type(self, request_mock):
        self.client.put('/url')
        eq_(request_mock.call_args_list, [
            mock.call('PUT', 'BASE_URL/url', headers={'Content-Type': 'application/json'})])

    @mock.patch('requests.request')
    def test_post_issues_a_POST_request_with_json_content_type(self, request_mock):
        self.client.post('/url')
        eq_(request_mock.call_args_list, [
            mock.call('POST', 'BASE_URL/url', headers={'Content-Type': 'application/json'})])

    @mock.patch('pylcp.api.generate_authorization_header_value', return_value='auth_value')
    @mock.patch('requests.request')
    def test_get_issues_a_GET_request_with_none_headers_and_none_params(self, request_mock, auth_header_mock):
        self.client.key_id = 'foobar'
        self.client.get('/url')
        eq_(request_mock.call_args_list, [
            mock.call('GET', 'BASE_URL/url', headers={'Authorization': 'auth_value'})])

    @mock.patch('requests.request')
    def test_get_issues_a_GET_request_with_headers_and_params(self, request_mock):
        self.client.get('/url', headers={'Header-Name': 'some header value'}, params={'paramName': 'some param value'})
        eq_(request_mock.call_args_list, [
            mock.call('GET', 'BASE_URL/url', headers={'Header-Name': 'some header value'},
                      params={'paramName': 'some param value'})])

    @mock.patch('pylcp.api.generate_authorization_header_value', return_value='auth_value')
    @mock.patch('requests.request')
    def test_specifying_key_id_causes_Authorization_header_to_be_set(self, request_mock, auth_header_mock):
        self.client.base_url = 'http://example.com'
        self.client.key_id = 'foobar'
        self.client.request('METHOD', '/url', headers={'Content-Type': 'application/json'})
        eq_(request_mock.call_args_list, [
            mock.call('METHOD', 'http://example.com/url', headers={
                'Content-Type': 'application/json',
                'Authorization': 'auth_value'})])

    @mock.patch('requests.request')
    def test_get_with_params_issues_a_GET_request_with_none_headers_and_optional_params(self, request_mock):
        self.client.get('/url', params="yada")
        eq_(request_mock.call_args_list, [
            mock.call('GET', 'BASE_URL/url', headers={}, params="yada")])

    def test_when_mask_sensitive_data_is_called_then_masking_happens_on_a_copy(self):
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

    @mock.patch('requests.request')
    @mock.patch('pylcp.api.mask_sensitive_data')
    def test_post_mask_data_is_called_a_POST_request_with_json_content_type(
            self, mock_mask_sensitive_data, request_mock):
        self.client.post('/url', data={"test": "test"})
        eq_(mock_mask_sensitive_data.call_args_list, [
            mock.call({'test': 'test'})])

    def assert_loggers_called(self, log_data):
        with mock.patch('pylcp.api.request_logger') as request_logger_mock:
            with mock.patch('pylcp.api.response_logger') as response_logger_mock:
                with mock.patch('requests.request') as request_mock:
                    class ResponseData:
                        status_code = 200
                        reason = 'REASON'
                        headers = {'HEADER_KEY': 'HEADER_VALUE'}
                        text = "{'answer': 42}"

                        def to_dict(self):
                            return {
                                'status_code': self.status_code,
                                'reason': self.reason,
                                'headers': api.format_headers(self.headers),
                                'body': self.text,
                            }

                    response_data = ResponseData()
                    request_mock.return_value = response_data
                    self.client.post('/url', data=log_data['body'])
                    eq_(
                        [mock.call(self.request_log_format_string, log_data)],
                        request_logger_mock.debug.call_args_list
                    )
                    eq_(
                        [mock.call(self.response_log_format_string, response_data.to_dict())],
                        response_logger_mock.debug.call_args_list
                    )

    def test_post_logs_with_json_data(self):
        log_data = {
            'url': 'BASE_URL/url',
            'headers': 'Content-Type: application/json',
            'body': {'answer': 42},
            'method': 'POST'
        }
        self.assert_loggers_called(log_data)

    def test_post_logs_with_non_json_data(self):
        log_data = {
            'url': 'BASE_URL/url',
            'headers': 'Content-Type: application/json',
            'body': 'This is not JSON',
            'method': 'POST'
        }
        self.assert_loggers_called(log_data)
