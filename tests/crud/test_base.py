import decimal
import httplib

import mock
from nose import tools
import requests

from pylcp import api
from pylcp.crud import crud
from tests.crud import base


class TestCrud(object):
    def test_populates_url_from_self_link(self):
        response_mock = base.mock_response(headers={}, body={'links': {'self': {'href': 'some_url'}}})
        lcp_obj = crud.LCPResource(response_mock)
        tools.assert_equal('some_url', lcp_obj.url)

    def test_populates_url_from_location_header(self):
        response_mock = base.mock_response(httplib.NO_CONTENT)
        lcp_obj = crud.LCPResource(response_mock)
        tools.assert_equal('http://example.com/foo/some_id', lcp_obj.url)

    def test_populates_id_from_url(self):
        lcp_obj = crud.LCPResource(base.mock_response())
        tools.assert_equal('some_id', lcp_obj.id)

    def test_url_is_none_when_no_self_link(self):
        response_mock = base.mock_response(headers={})
        lcp_obj = crud.LCPResource(response_mock)
        tools.assert_equal(None, lcp_obj.url)

    def test_url_is_none_when_no_response(self):
        lcp_obj = crud.LCPResource()
        tools.assert_equal(None, lcp_obj.url)


class TestLCPCRUD(object):
    def setup(self):
        self.mock_client = mock.create_autospec(api.Client)
        self.lcp_crud = crud.LCP(self.mock_client)

    def test_lcp_resource(self):
        tools.assert_equal(crud.LCPResource, self.lcp_crud.resource_class)

    def test_create(self):
        mocked_response = base.mock_response(headers={}, body=base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        response = self.lcp_crud.create(base.SAMPLE_URL, {})

        tools.assert_equal(1, self.mock_client.post.call_count)
        base.assert_lcp_resource(mocked_response, response)

    def test_read(self):
        mocked_response = base.mock_response(headers={}, body=base.SAMPLE_RESPONSE)
        self.mock_client.get.return_value = mocked_response

        response = self.lcp_crud.read(base.SAMPLE_URL)
        tools.assert_equal(1, self.mock_client.get.call_count)
        base.assert_lcp_resource(mocked_response, response)

    def test_update(self):
        mocked_response = base.mock_response(headers={}, body=base.SAMPLE_RESPONSE)
        self.mock_client.put.return_value = mocked_response

        response = self.lcp_crud.update(base.SAMPLE_URL, {})
        tools.assert_equal(1, self.mock_client.put.call_count)
        base.assert_lcp_resource(mocked_response, response)

    def test_delete(self):
        mocked_response = base.mock_response(headers={}, body=base.SAMPLE_RESPONSE)
        self.mock_client.put.return_value = mocked_response

        response = self.lcp_crud.update(base.SAMPLE_URL, {})
        tools.assert_equal(1, self.mock_client.put.call_count)
        base.assert_lcp_resource(mocked_response, response)

    def test_search(self):
        mocked_response = base.mock_response(headers={}, body=base.SAMPLE_RESPONSE)
        self.mock_client.get.return_value = mocked_response
        query_params = {'a': 'b'}

        response = self.lcp_crud.search(base.SAMPLE_URL, query_params)
        tools.assert_equal(1, self.mock_client.get.call_count)
        base.assert_lcp_resource(mocked_response, response)

    def test_search_no_params(self):
        mocked_response = base.mock_response(headers={}, body=base.SAMPLE_RESPONSE)
        self.mock_client.get.return_value = mocked_response

        response = self.lcp_crud.search(base.SAMPLE_URL)
        tools.assert_equal(1, self.mock_client.get.call_count)
        base.assert_lcp_resource(mocked_response, response)


class TestCrudErrors(object):
    def test_create_exception_with_no_request_payload_returns_exception_with_empty_request(self):
        response_mock = mock.Mock(spec=requests.Response)
        response_mock.headers = {}
        response_mock.text = "text"
        response_mock.status_code = httplib.NOT_FOUND

        crud_error = crud.CRUDError(crud.CRUDError, '/path/', 'POST', response_mock)

        tools.assert_equal('CRUDError returned 404.\nOperation: POST\n'
                           'Correlation ID: none\nURL: /path/\nResponse: text',
                           crud_error.message)

    def test_create_exception_with_request_payload_returns_exception_with_request_payload(self):
        response_mock = mock.Mock(spec=requests.Response)
        response_mock.headers = {}
        response_mock.text = "text"
        response_mock.status_code = httplib.NOT_FOUND

        crud_error = crud.CRUDError(crud.CRUDError, '/path/', 'POST', response_mock, 'some_payload')

        tools.assert_equal('CRUDError returned 404.\nOperation: POST\n'
                           'Correlation ID: none\nURL: /path/\nRequest: "some_payload"\nResponse: text',
                           crud_error.message)

    def test_create_exception_with_request_payload_containing_decimal_data_returns_exception_with_request(self):
        response_mock = mock.Mock(spec=requests.Response)
        response_mock.headers = {}
        response_mock.text = "text"
        response_mock.status_code = httplib.NOT_FOUND
        request_payload = {'decimal': decimal.Decimal('3.15')}

        crud_error = crud.CRUDError(crud.CRUDError, '/path/', 'POST', response_mock, request_payload)

        tools.assert_equal('CRUDError returned 404.\nOperation: POST\n'
                           'Correlation ID: none\nURL: /path/\nRequest: {\n  "decimal": 3.15\n}\nResponse: text',
                           crud_error.message)

    def test_create_exception_with_request_parameters_returns_exception_with_parameters(self):
        response_mock = mock.Mock(spec=requests.Response)
        response_mock.headers = {}
        response_mock.text = "text"
        response_mock.status_code = httplib.NOT_FOUND

        crud_error = crud.CRUDError(crud.CRUDError, '/path/', 'POST', response_mock, request_parameters={'a': 'b'})

        tools.assert_equal('CRUDError returned 404.\nOperation: POST\n'
                           'Correlation ID: none\nURL: /path/\nRequest Parameters: {\n  "a": "b"\n}\nResponse: text',
                           crud_error.message)
