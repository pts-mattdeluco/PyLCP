from nose.tools import eq_
import mock

from lcp import api


@mock.patch('lcp.api.requests.request')
def _assert_calls_requests_with_url(original_url, expected_url, request_mock):
    api.Client('BASE_URL').request('METHOD', original_url)
    expected_headers = {'Content-Type': 'application/json'}
    eq_(request_mock.call_args_list, [
        mock.call('METHOD', expected_url, data='{}', headers=expected_headers)])


def test_request_does_not_alter_absolute_urls():
    for absolute_url in [
            'http://www.points.com',
            'https://www.points.com',
            ]:
        yield _assert_calls_requests_with_url, absolute_url, absolute_url


def test_request_adds_base_url_to_relative_urls():
    for absolute_url in [
            'some/relative/path/',
            '/some/absolute/path',
            ]:
        yield _assert_calls_requests_with_url, absolute_url, 'BASE_URL' + absolute_url
