.. _testing:

Testing
=======

When testing your LCP client application, you can use the
:class:`MockRequestAdapter <pylcp.testing.MockRequestAdapter>` to
capture LCP requests without actually sending the request to 
the LCP. You can use methods on the adapter to assert attributes
of the request such as the value of headers. 
:class:`MockRequestAdapter <pylcp.testing.MockRequestAdapter>` is
a specialization of :class:`requests.adapters.BaseAdapter`.

For example, given this application code:

::

    from pylcp import api


    def get_lcp_account(client, account_id):
        response = client.get(
            '/accounts/' + account_id,
            headers={'Accept': 'application/json'}
        )
        response.raise_for_status()
        return response

The following code tests that the request to the LCP is correct. The
adapter captures the request before it is sent to the LCP and 
provides some basic assertions.

::

    import unittest

    from pylcp import testing


    class TestGetLCPAccount(unittest.TestCase):
        def setUp(self):
            self.client = api.Client(
                'https://lcp.points.com/v1',
                key_id='my-key-id',
                shared_secret='my-shared-secret'
            )
            self.adapter = testing.MockRequestAdapter()
            self.client.mount('https://', self.adapter)

        def test_get_sets_accept_header(self):
            get_lcp_account(self.client, 'my-account-id')

            self.adapter.assert_headers_present({
                'Accept': 'application/json'
            })

        def test_gets_account_id(self):
            get_lcp_account(self.client, 'my-account-id')

            self.adapter.assert_request_properties(
                method='GET',
                url='https://lcp.points.com/v1/accounts/my-account-id'
            )

.. autoclass:: pylcp.testing.MockRequestAdapter
    :members:
