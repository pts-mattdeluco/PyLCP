from nose.tools import eq_
import mock

from lcp import api


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
