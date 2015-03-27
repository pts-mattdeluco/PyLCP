import mock
from nose import tools

from pylcp import api
from pylcp.crud import loyalty_program
from tests.crud import base as test_base


class TestLoyaltyProgramCRUD(object):
    def setup(self):
        self.mock_client = mock.create_autospec(api.Client)
        self.lps_crud = loyalty_program.LoyaltyProgram(self.mock_client)


    def test_get_loyalty_program(self):
        mocked_response = test_base.mock_response(headers={}, body=test_base.SAMPLE_RESPONSE)
        self.mock_client.get.return_value = mocked_response

        response = self.lps_crud.read('lp123')

        tools.assert_equal(1, self.mock_client.get.call_count)
        self.mock_client.get.assert_called_with('/lps/lp123', data=None, params=None)
        test_base.assert_lcp_resource(mocked_response, response)
