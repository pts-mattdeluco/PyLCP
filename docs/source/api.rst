.. _api:

Developer Interface
===================

Sending Requests
----------------

All requests to the LCP can be sent using an instance of the :class:`Client <pylcp.api.Client>`
class configured with the appropriate credentials. A :class:`Client <pylcp.api.Client>`
is based on a :class:`requests.Session` and behaves very similarly. 

The most significant 
difference is that request URLs are path fragments and are effectively appended to
the base URL provided on the constructor.

For example, the following code:

::

    client = pylcp.api.Client(
        'https://lcp.points.com/v1',
        key_id='my-key-id', 
        shared_secret='my-secret'
    )
    response = client.get('/accounts/my-account-id')

sends the `GET` request to `https://lcp.points.com/v1/accounts/my-account-id`.

In addition, the client will log the headers and body of every request.

.. autoclass:: pylcp.api.Client
    :members:

Logging
-------

The headers and bodies for all requests and responses are logged using the
loggers `pylcp.api.request_logger` and `pylcp.api.response_logger`
respectively. The loggers are created for you, but you must configure these 
with the desired handlers, levels, etc. Requests and responses are 
logged at the `DEBUG` level.

The following functions can be used to mask credit card data in your
app. They implement the same masking rules applied when logging client request
and response data.

.. autofunction:: pylcp.api.mask_credit_card_number
.. autofunction:: pylcp.api.mask_credit_card_number_with_bin
.. autofunction:: pylcp.api.mask_sensitive_billing_info_data

Request Signing
---------------

In general, the request signing performed by the methods on the 
:class:`Client <pylcp.api.Client>` class should be sufficient in most, 
if not all scenarios. The `pylcp.mac`
module has several functions that perform the various steps of request signing.

.. autofunction:: pylcp.mac.build_normalized_request_string
.. autofunction:: pylcp.mac.generate_authorization_header_value
.. autofunction:: pylcp.mac.generate_ext
.. autofunction:: pylcp.mac.generate_nonce
.. autofunction:: pylcp.mac.generate_signature

:ref:`modindex`
