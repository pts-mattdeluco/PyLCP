Python Client Library for the Points Loyalty Commerce Platform
==============================================================

[![Build Status](https://travis-ci.org/Points/PyLCP.svg?branch=master)](https://travis-ci.org/Points/PyLCP)

This library provides a simple interface for submitting signed 
requests to the Points Loyalty Commerce Platform (LCP):

The example below shows how to submit a signed request to the LCP:

```python
	from pylcp.api import Client

	client = Client('https://lcp.points.com/v1',
					key_id='my_mac_key_identifier',
					shared_secret='my_mac_key')
	response = client.get('/accounts/my_account_id')
```

References
----------
For further information on the Loyalty Commerce Platform, check out 
the [Getting Started Guide](http://points.github.io/Loyalty-Commerce-Platform/index.html).

The PyLCP library uses the [Requests](http://www.python-requests.org/en/latest/)
library for sending HTTP requests to the
LCP. In particular, responses are instances of the 
[requests.Response](http://docs.python-requests.org/en/latest/api/#requests.Response) class.

Developer Notes
---------------

To get started:

    (create a virtual environment)
    pip install -r requirements-dev.txt

To run tests:

    nosetests

To check code style:

    flake8

To install a local copy of the code in to a virtual environment (for testing
changes to PyLCP in your LCP App project):

    python setup.py develop

