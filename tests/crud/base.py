import httplib

import mock
from nose import tools
import requests

from pylcp.crud import base

SAMPLE_URL = 'http://test.com/test'
SAMPLE_RESPONSE = {'links': {'self': {'href': 'some_url'}}}


def mock_response(status_code=httplib.OK, headers=None, body=None):
    response_mock = mock.Mock(spec=requests.Response)
    response_mock.headers = headers if headers is not None else {'location': 'http://example.com/foo/some_id'}
    response_mock.json.return_value = body if body is not None else {}
    response_mock.status_code = status_code
    return response_mock


def assert_lcp_resource(mocked_response, response):
    tools.assert_is_instance(response, base.LCPResource)
    tools.assert_equal(mocked_response, response.response)
