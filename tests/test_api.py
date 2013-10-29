from nose.tools import eq_
import mock

from lcp import api
from lcp import context


class TestApiClient(object):
    def setup(self):
        self.client = api.Client('BASE_URL')

    def test_request_does_not_alter_absolute_urls(self):
        for absolute_url in [
                'http://www.points.com',
                'https://www.points.com']:
            yield self._assert_calls_requests_with_url, absolute_url, absolute_url

    def test_request_adds_base_url_to_relative_urls(self):
        for absolute_url in [
                'some/relative/path/',
                '/some/absolute/path']:
            yield self._assert_calls_requests_with_url, absolute_url, 'BASE_URL' + absolute_url

    @mock.patch('lcp.api.requests.request')
    def _assert_calls_requests_with_url(self, original_url, expected_url, request_mock):
        self.client.request('METHOD', original_url)
        eq_(request_mock.call_args_list, [
            mock.call('METHOD', expected_url)])

    @mock.patch('lcp.api.requests.request')
    def test_delete_issues_a_DELETE_request_with_empty_headers(self, request_mock):
        self.client.delete('/url')
        eq_(request_mock.call_args_list, [
            mock.call('DELETE', 'BASE_URL/url', headers={})])

    @mock.patch('lcp.api.requests.request')
    def test_put_issues_a_PUT_request_with_json_content_type(self, request_mock):
        self.client.put('/url')
        eq_(request_mock.call_args_list, [
            mock.call('PUT', 'BASE_URL/url', headers={'Content-Type': 'application/json'})])

    @mock.patch('lcp.api.requests.request')
    def test_post_issues_a_POST_request_with_json_content_type(self, request_mock):
        self.client.post('/url')
        eq_(request_mock.call_args_list, [
            mock.call('POST', 'BASE_URL/url', headers={'Content-Type': 'application/json'})])

    @mock.patch('lcp.api.requests.request')
    def test_get_issues_a_GET_request_with_empty_headers_and_no_params(self, request_mock):
        self.client.get('/url')
        eq_(request_mock.call_args_list, [
            mock.call('GET', 'BASE_URL/url', headers={}, params=None)])

    @mock.patch('lcp.api.generate_authorization_header_value', return_value='auth_value')
    @mock.patch('lcp.api.requests.request')
    def test_specifying_key_id_causes_Authorization_header_to_be_set(self, request_mock, auth_header_mock):
        self.client.base_url = 'http://example.com'
        self.client.key_id = 'key_id'
        self.client.request('METHOD', '/url', headers={'Content-Type': 'application/json'})
        eq_(request_mock.call_args_list, [
            mock.call('METHOD', 'http://example.com/url', headers={
                'Content-Type': 'application/json',
                'Authorization': 'auth_value'})])

    @mock.patch('lcp.api.requests.request')
    def test_get_with_params_issues_a_GET_request_with_empty_headers_and_optional_params(self, request_mock):
        self.client.get('/url', params="yada")
        eq_(request_mock.call_args_list, [
            mock.call('GET', 'BASE_URL/url', headers={}, params="yada")])

    @mock.patch('lcp.api.requests.request')
    def test_internal_client_adds_additional_headers(self, request_mock):
        internal_client = api.InternalClient('BASE_URL')
        internal_client.request('METHOD', '/url', foo='bar')
        eq_(request_mock.call_args_list, [
            mock.call('METHOD', 'BASE_URL/url', foo='bar',
                      headers={
                                context.HEADERS_MODE: context.MODE_LIVE,
                                context.HEADERS_EXTERNAL_BASE_URL: 'BASE_URL'})])
