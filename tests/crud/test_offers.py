import copy

import mock
from nose import tools

from pylcp import api
from pylcp.crud import offers
from tests.crud import base


class TestOfferSetCRUD(object):
    def setup(self):
        self.mock_client = mock.create_autospec(api.Client)
        self.offer_set_crud = offers.OfferSet(self.mock_client)
        self.member_details = {
            "firstName": "Frank",
            "lastName": "Caron",
            "memberId": "123123",
            "membershipLevel": "G1",
            "balance": 1234,
            "memberValidation": "https://lcp.points.com/v1/lps/1/mvs/3"
        }

        self.session = offers.Session(channel="storefront",
                                      referralCode='abc',
                                      clientIpAddress='127.0.0.1',
                                      clientUserAgent="FAST-WebCrawler/3.x Multimedia")

        self.offer_types = ["BUY", "GIFT"]

    def test_create_offerset_with_recipient(self):
        recipient_details = copy.deepcopy(self.member_details)
        recipient_details['memberId'] = '456456'

        mocked_response = base.mock_response(headers={}, body=base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        response = self.offer_set_crud.create(base.SAMPLE_URL,
                                              self.offer_types,
                                              self.session,
                                              self.member_details,
                                              recipient_details)

        tools.assert_equal(1, self.mock_client.post.call_count)
        base.assert_lcp_resource(mocked_response, response)

    def test_create_offerset_without_recipient(self):
        mocked_response = base.mock_response(headers={}, body=base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        response = self.offer_set_crud.create(base.SAMPLE_URL, self.offer_types, self.session, self.member_details)

        tools.assert_equal(1, self.mock_client.post.call_count)
        base.assert_lcp_resource(mocked_response, response)

    def test_create_offer_set_with_optional_kwargs_add_top_level_params(self):
        mocked_response = base.mock_response(headers={}, body=base.SAMPLE_RESPONSE)
        self.mock_client.post.return_value = mocked_response

        additional_params = {'a': 'b', 'c': 'd'}

        response = self.offer_set_crud.create(base.SAMPLE_URL,
                                              self.offer_types,
                                              self.session,
                                              self.member_details,
                                              **additional_params)

        tools.assert_equal(1, self.mock_client.post.call_count)
        base.assert_lcp_resource(mocked_response, response)

    def test_format_payload_with_recipient(self):
        recipient_details = copy.deepcopy(self.member_details)
        recipient_details['memberId'] = '456456'

        expected_payload = {'offerTypes': self.offer_types,
                            'session': self.session,
                            'user': self.member_details,
                            'recipient': recipient_details}
        payload = self.offer_set_crud._create_payload(self.offer_types,
                                                      self.session,
                                                      self.member_details,
                                                      recipient_details)

        tools.assert_equal(expected_payload, payload)

    def test_format_payload_no_recipient(self):
        expected_payload = {'offerTypes': self.offer_types,
                            'session': self.session,
                            'user': self.member_details}
        payload = self.offer_set_crud._create_payload(self.offer_types, self.session, self.member_details, None)

        tools.assert_equal(expected_payload, payload)

    def test_format_payload_with_optional_kwargs_adds_parameters_to_top_level(self):
        additional_params = {'a': 'b', 'c': 'd'}

        expected_payload = {'offerTypes': self.offer_types,
                            'session': self.session,
                            'user': self.member_details,
                            'a': 'b',
                            'c': 'd'}

        payload = self.offer_set_crud._create_payload(self.offer_types,
                                                      self.session,
                                                      self.member_details,
                                                      None,
                                                      **additional_params)

        tools.assert_equal(expected_payload, payload)
