from future import standard_library
standard_library.install_aliases()  # NOQA

from builtins import object
import decimal
import http.client

import mock
from nose import tools
import requests

from pylcp import api
from pylcp.crud import base as crud
from tests.crud import base as test_base


class TestLCPResource(object):
    def test_populates_url_from_self_link(self):
        response_mock = test_base.mock_response(headers={}, body={'links': {'self': {'href': 'some_url'}}})
        lcp_obj = crud.LCPResource(response_mock)
        tools.assert_equal('some_url', lcp_obj.url)

    def test_populates_url_from_location_header(self):
        response_mock = test_base.mock_response(http.client.NO_CONTENT)
        lcp_obj = crud.LCPResource(response_mock)
        tools.assert_equal('http://example.com/foo/some_id', lcp_obj.url)

    def test_url_is_none_when_no_self_link(self):
        response_mock = test_base.mock_response(headers={})
        lcp_obj = crud.LCPResource(response_mock)
        tools.assert_equal(None, lcp_obj.url)

    def test_url_is_none_when_no_response(self):
        lcp_obj = crud.LCPResource()
        tools.assert_equal(None, lcp_obj.url)

    def test_getitem_gets_from_response(self):
        response_mock = test_base.mock_response(headers={}, body={'links': {'self': {'href': 'some_url'}}})
        lcp_obj = crud.LCPResource(response_mock)
        tools.assert_equal('some_url', lcp_obj['links']['self']['href'])

    def test_setitem_raises(self):
        response_mock = test_base.mock_response(headers={}, body={'links': {'self': {'href': 'some_url'}}})
        with tools.assert_raises(TypeError):
            crud.LCPResource(response_mock)['links'] = 'foo'

    def test_json_returns_copy_of_response(self):
        response_mock = test_base.mock_response(headers={}, body={'links': {'self': {'href': 'some_url'}}})
        lcp_obj = crud.LCPResource(response_mock)
        json_copy = lcp_obj.json
        json_copy['links'] = 'foo'
        tools.assert_equal('some_url', lcp_obj['links']['self']['href'])


class TestLCPCRUD(object):
    def setup(self):
        self.mock_client = mock.create_autospec(api.Client)
        self.lcp_crud = crud.LCPCrud(self.mock_client)

    def test_create(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        response = self.lcp_crud.create(test_base.SAMPLE_URL, {})

        tools.assert_equal(1, self.mock_client.post.call_count)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_request_failures_raises_crud_error(self):
        mocked_response = test_base.mock_response(status_code=http.client.NOT_FOUND)
        self.mock_client.post.return_value = mocked_response
        with tools.assert_raises(crud.CRUDError):
            self.lcp_crud.create(test_base.SAMPLE_URL, {})

    def test_read(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.get.return_value = mocked_response

        response = self.lcp_crud.read(test_base.SAMPLE_URL)
        tools.assert_equal(1, self.mock_client.get.call_count)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_update(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.put.return_value = mocked_response

        response = self.lcp_crud.update(test_base.SAMPLE_URL, {})
        tools.assert_equal(1, self.mock_client.put.call_count)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_delete(self):
        mocked_response = test_base.mock_response(status_code=http.client.NO_CONTENT)
        self.mock_client.delete.return_value = mocked_response

        response = self.lcp_crud.delete(test_base.SAMPLE_URL)
        tools.assert_equal(1, self.mock_client.delete.call_count)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_search(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.get.return_value = mocked_response
        query_params = {'a': 'b'}

        response = self.lcp_crud.search(test_base.SAMPLE_URL, query_params)
        tools.assert_equal(1, self.mock_client.get.call_count)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_search_no_params(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.get.return_value = mocked_response

        response = self.lcp_crud.search(test_base.SAMPLE_URL)
        tools.assert_equal(1, self.mock_client.get.call_count)
        test_base.assert_lcp_resource(mocked_response, response)


class TestCrudErrors(object):
    def test_create_exception_with_no_request_payload_returns_exception_with_empty_request(self):
        response_mock = mock.Mock(spec=requests.Response)
        response_mock.headers = {}
        response_mock.text = "text"
        response_mock.status_code = http.client.NOT_FOUND

        crud_error = crud.CRUDError('/path/', 'POST', response_mock)

        tools.assert_equal('404 returned.\nMethod: POST\n'
                           'Correlation ID: none\nURL: /path/\nResponse: text',
                           crud_error.message)

    def test_create_exception_with_request_payload_returns_exception_with_request_payload(self):
        response_mock = mock.Mock(spec=requests.Response)
        response_mock.headers = {}
        response_mock.text = "text"
        response_mock.status_code = http.client.NOT_FOUND

        crud_error = crud.CRUDError('/path/', 'POST', response_mock, **{'request_payload': 'some_payload'})

        tools.assert_equal('404 returned.\nMethod: POST\n'
                           'Correlation ID: none\nURL: /path/\nRequest payload: "some_payload"\nResponse: text',
                           crud_error.message)

    def test_create_exception_with_request_payload_containing_decimal_data_returns_exception_with_request(self):
        response_mock = mock.Mock(spec=requests.Response)
        response_mock.headers = {}
        response_mock.text = "text"
        response_mock.status_code = http.client.NOT_FOUND
        request_payload = {'decimal': decimal.Decimal('3.15')}

        crud_error = crud.CRUDError('/path/', 'POST', response_mock, **{'request_payload': request_payload})

        tools.assert_equal('404 returned.\nMethod: POST\n'
                           'Correlation ID: none\nURL: /path/\nRequest payload: {\n  "decimal": 3.15\n}\n'
                           'Response: text',
                           crud_error.message)

    def test_create_exception_with_request_parameters_returns_exception_with_parameters(self):
        response_mock = mock.Mock(spec=requests.Response)
        response_mock.headers = {}
        response_mock.text = "text"
        response_mock.status_code = http.client.NOT_FOUND

        crud_error = crud.CRUDError('/path/', 'POST', response_mock, **{'request_parameters': {'a': 'b'}})

        tools.assert_equal('404 returned.\nMethod: POST\n'
                           'Correlation ID: none\nURL: /path/\nRequest parameters: {\n  "a": "b"\n}\nResponse: text',
                           crud_error.message)
