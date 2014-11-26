import copy

import mock
from nose import tools

from pylcp import api
from pylcp.crud import postings
from tests.crud import base as test_base


class TestCredit(object):
    def setup(self):
        self.mock_client = mock.create_autospec(api.Client)
        self.credit_crud = postings.Credit(self.mock_client)

        self.amount = 1000
        self.mv_url = '/lps/123/mvs/456'
        self.pic = 'abc'
        self.additional_params = {'a': 'b', 'c': 'd'}
        self.path = '/lps/123/payments'
        self.expected_payload = {'amount': 1000, 'memberValidation': '/lps/123/mvs/456'}

    def test_create_credit_no_pic(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        response = self.credit_crud.create(self.path, self.amount, self.mv_url)

        tools.assert_equal(1, self.mock_client.post.call_count)
        self.mock_client.post.assert_called_with(self.path, data=self.expected_payload, params=None)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_create_credit_with_optional_pic(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        expected_payload = copy.deepcopy(self.expected_payload)
        expected_payload['pic'] = self.pic

        response = self.credit_crud.create(self.path, self.amount, self.mv_url, pic=self.pic)

        tools.assert_equal(1, self.mock_client.post.call_count)
        self.mock_client.post.assert_called_with(self.path, data=expected_payload, params=None)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_create_credit_with_optional_kwargs_add_top_level_params(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        expected_payload = copy.deepcopy(self.expected_payload)
        expected_payload.update(self.additional_params)

        response = self.credit_crud.create(self.path, self.amount, self.mv_url, **self.additional_params)

        tools.assert_equal(1, self.mock_client.post.call_count)
        self.mock_client.post.assert_called_with(self.path, data=expected_payload, params=None)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_create_payload(self):
        expected_payload = {"amount": self.amount, "memberValidation": self.mv_url}
        payload = self.credit_crud._create_payload(self.amount, self.mv_url)

        tools.assert_equal(expected_payload, payload)

    def test_create_payload_with_optional_pic(self):
        expected_payload = {"amount": self.amount, "memberValidation": self.mv_url, "pic": self.pic}
        payload = self.credit_crud._create_payload(self.amount, self.mv_url, self.pic)

        tools.assert_equal(expected_payload, payload)

    def test_create_payload_with_empty_pic(self):
        expected_payload = {"amount": self.amount, "memberValidation": self.mv_url, "pic": ''}
        payload = self.credit_crud._create_payload(self.amount, self.mv_url, '')

        tools.assert_equal(expected_payload, payload)

    def test_create_payload_with_optional_kwargs(self):
        expected_payload = {"amount": self.amount, "memberValidation": self.mv_url, 'a': 'b', 'c': 'd'}
        payload = self.credit_crud._create_payload(self.amount, self.mv_url, **self.additional_params)

        tools.assert_equal(expected_payload, payload)
