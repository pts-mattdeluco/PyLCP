from future import standard_library
standard_library.install_aliases()  # NOQA

from builtins import bytes
try:
    from http.client import OK
except ImportError:
    from httplib import OK
import json

from nose import tools
import requests

from pylcp.api import JsonResponseWrapper
from pylcp.crud import base

SAMPLE_URL = 'http://test.com/test'
SAMPLE_RESPONSE = {'links': {'self': {'href': 'some_url'}}}


def mock_response(status_code=OK, headers=None, body=None):
    response_mock = requests.Response()
    response_mock.headers = headers if headers is not None else {'location': 'http://example.com/foo/some_id'}
    if body is None:
        body = {}
    response_mock._content = bytes(json.dumps(body).encode('utf-8'))
    response_mock.status_code = status_code
    return response_mock


def mock_response_with_json_response_wrapper(status_code=OK, headers=None, body=None):
    response_mock = mock_response(status_code, headers, body)
    return JsonResponseWrapper(response_mock)


def assert_lcp_resource(mocked_response, response):
    tools.assert_is_instance(response, base.LCPResource)
    tools.assert_equal(mocked_response, response.response)
