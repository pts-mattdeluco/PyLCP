import mock
from nose import tools

from pylcp import api
from pylcp.crud import payment
from tests.crud import base


class TestPaymentAuthCRUD(object):
    def setup(self):
        self.mock_client = mock.create_autospec(api.Client)
        self.payment_crud = payment.PaymentAuth(self.mock_client)

    def test_create_payment(self):
        mocked_response = base.mock_response(headers={}, body=base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        test_payload = {'test': 'data'}

        response = self.payment_crud.create(base.SAMPLE_URL, test_payload)

        tools.assert_equal(1, self.mock_client.post.call_count)
        base.assert_lcp_resource(mocked_response, response)


class TestPaymentCaptureCRUD(object):
    def setup(self):
        self.mock_client = mock.create_autospec(api.Client)
        self.payment_crud = payment.PaymentCapture(self.mock_client)

    def test_create_payment(self):
        mocked_response = base.mock_response(headers={}, body=base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        response = self.payment_crud.create(base.SAMPLE_URL)

        tools.assert_equal(1, self.mock_client.post.call_count)
        base.assert_lcp_resource(mocked_response, response)
