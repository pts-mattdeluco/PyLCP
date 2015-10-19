from builtins import object
import copy

try:
    from unittest import mock
except ImportError:
    import mock
from nose import tools

from pylcp import api
from pylcp.crud import orders
from tests.crud import base as test_base


class TestOrdersCRUD(object):
    def setup(self):
        self.mock_client = mock.create_autospec(api.Client)
        self.orders_crud = orders.Order(self.mock_client)

        self.order_type = "buy"
        self.data = {'language': 'en'}
        self.additional_params = {'a': 'b', 'c': 'd'}

        self.expected_payload = {'orderType': 'buy', 'data': {'language': 'en'}}

    def test_create_order(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        response = self.orders_crud.create(self.order_type, self.data)

        tools.assert_equal(1, self.mock_client.post.call_count)
        self.mock_client.post.assert_called_with('/orders/', data=self.expected_payload, params=None)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_create_order_with_optional_kwargs_add_top_level_params(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        expected_payload = copy.deepcopy(self.expected_payload)
        expected_payload.update(self.additional_params)

        response = self.orders_crud.create(self.order_type, self.data, **self.additional_params)

        tools.assert_equal(1, self.mock_client.post.call_count)
        self.mock_client.post.assert_called_with('/orders/', data=expected_payload, params=None)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_create_payload(self):
        expected_payload = {"orderType": self.order_type, "data": self.data}
        payload = self.orders_crud._create_payload(self.order_type, self.data)

        tools.assert_equal(expected_payload, payload)

    def test_create_payload_with_kwargs(self):
        expected_payload = {"orderType": self.order_type, "data": self.data, 'a': 'b', 'c': 'd'}

        payload = self.orders_crud._create_payload(self.order_type, self.data, **self.additional_params)

        tools.assert_equal(expected_payload, payload)
