import mock
from nose import tools

from pylcp import api
from pylcp.crud import payment
from tests.crud import base as test_base


class TestPaymentAuthCRUD(object):
    def setup(self):
        self.mock_client = mock.create_autospec(api.Client)
        self.payment_crud = payment.PaymentAuth(self.mock_client)
        self.path = '/lps/123/payments'

    def test_create_payment(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        test_payload = {'test': 'data'}

        response = self.payment_crud.create(self.path, test_payload)

        tools.assert_equal(1, self.mock_client.post.call_count)
        self.mock_client.post.assert_called_with(self.path, data=test_payload, params=None)
        test_base.assert_lcp_resource(mocked_response, response)


class TestPaymentCaptureCRUD(object):
    def setup(self):
        self.mock_client = mock.create_autospec(api.Client)
        self.payment_crud = payment.PaymentCapture(self.mock_client)
        self.path = '/lps/123/payments'

    def test_create_payment(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        response = self.payment_crud.create(self.path)

        tools.assert_equal(1, self.mock_client.post.call_count)
        self.mock_client.post.assert_called_with(self.path, data='{}', params=None)
        test_base.assert_lcp_resource(mocked_response, response)
