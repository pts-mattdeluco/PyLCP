Python Client Library for Points Loyalty Commerce Platform
==========================================================

This library provides a simple interface for submitting signed and unsigned
requests to the Points Loyalty Commerce Platform (LCP):

The example below shows how to submit an unsigned request to the LCP:

	from pylcp.api import Client

	client = Client('https://lcp.points.com/v1')
	response = client.post('/accounts/', data='{"email": "my_email@example.com"}')

The example below shows how to submit a signed request to the LCP:

	from pylcp.api import Client

	client = Client('https://lcp.points.com/v1',
					key_id='my_mac_key_identifier',
					shared_secret='my_mac_key')
	response = client.get('/accounts/my_account_id')

References
----------
For further information on the Loyalty Commerce Platform, see
http://points.github.io/Loyalty-Commerce-Platform/index.html

The PyLCP library uses the Requests library for sending HTTP requests to the
LCP. In particular, responses are instances of the requests.Response class.
For details on this library, see http://www.python-requests.org/en/latest/

Developer Note
--------------
We want to open source this package on github eventually and for this reason would
like to keep the footprint small. Hence pylcp is built minimally using setuptools.
