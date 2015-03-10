import copy

import mock
from nose import tools

from pylcp import api
from pylcp.crud import postings
from tests.crud import base as test_base


AMOUNT = 1000
MV_URL = '/lps/123/mvs/456'
PIC = 'abc'
ADDITIONAL_PARAMS = {'a': 'b', 'c': 'd'}
PATH = '/lps/123/payments'
EXPECTED_PAYLOAD = {'amount': 1000, 'memberValidation': '/lps/123/mvs/456'}


class PostingTestBase(object):
    def setup(self):
        self.mock_client = mock.create_autospec(api.Client)
        self.posting_crud = None

    def test_create_posting_with_optional_pic(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        expected_payload = copy.deepcopy(EXPECTED_PAYLOAD)
        expected_payload['pic'] = PIC

        response = self.posting_crud.create(PATH, AMOUNT, MV_URL, pic=PIC)

        tools.assert_equal(1, self.mock_client.post.call_count)
        self.mock_client.post.assert_called_with(PATH, data=expected_payload, params=None)
        test_base.assert_lcp_resource(mocked_response, response)


class TestPosting(PostingTestBase):
    def setup(self):
        super(TestPosting, self).setup()
        self.posting_crud = postings.Posting(self.mock_client)

    def test_create_posting_no_pic(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        response = self.posting_crud.create(PATH, AMOUNT, MV_URL)

        tools.assert_equal(1, self.mock_client.post.call_count)
        self.mock_client.post.assert_called_with(PATH, data=EXPECTED_PAYLOAD, params=None)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_create_posting_with_optional_kwargs_add_top_level_params(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        expected_payload = copy.deepcopy(EXPECTED_PAYLOAD)
        expected_payload.update(ADDITIONAL_PARAMS)

        response = self.posting_crud.create(PATH, AMOUNT, MV_URL, **ADDITIONAL_PARAMS)

        tools.assert_equal(1, self.mock_client.post.call_count)
        self.mock_client.post.assert_called_with(PATH, data=expected_payload, params=None)
        test_base.assert_lcp_resource(mocked_response, response)

    def test_posting_payload(self):
        expected_payload = {"amount": AMOUNT, "memberValidation": MV_URL}
        payload = self.posting_crud._create_payload(AMOUNT, MV_URL)

        tools.assert_equal(expected_payload, payload)

    def test_posting_payload_with_optional_pic(self):
        expected_payload = {"amount": AMOUNT, "memberValidation": MV_URL, "pic": PIC}
        payload = self.posting_crud._create_payload(AMOUNT, MV_URL, PIC)

        tools.assert_equal(expected_payload, payload)

    def test_posting_payload_with_empty_pic(self):
        expected_payload = {"amount": AMOUNT, "memberValidation": MV_URL, "pic": ''}
        payload = self.posting_crud._create_payload(AMOUNT, MV_URL, '')

        tools.assert_equal(expected_payload, payload)

    def test_posting_payload_with_optional_kwargs(self):
        expected_payload = {"amount": AMOUNT, "memberValidation": MV_URL, 'a': 'b', 'c': 'd'}
        payload = self.posting_crud._create_payload(AMOUNT, MV_URL, **ADDITIONAL_PARAMS)

        tools.assert_equal(expected_payload, payload)


class TestDebit(PostingTestBase):
    def setup(self):
        super(TestDebit, self).setup()
        self.posting_crud = postings.Debit(self.mock_client)


class TestCredit(PostingTestBase):
    def setup(self):
        super(TestCredit, self).setup()
        self.posting_crud = postings.Credit(self.mock_client)
