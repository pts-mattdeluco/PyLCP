Python Client Library for the Points Loyalty Commerce Platform
==============================================================

This library provides a simple interface for submitting signed and unsigned
requests to the Points Loyalty Commerce Platform (LCP):

The example below shows how to submit an unsigned request to the LCP:

```python
	from pylcp.api import Client

	client = Client('https://lcp.points.com/v1')
	response = client.post('/accounts/', data='{"email": "my_email@example.com"}')
```

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
We want to eventually open source this package by making the GitHub repository public. We would
like to keep the footprint small and use tools for building and testing that
will be familiar to most Python developers. Hence PyLCP is built minimally
using setuptools and does not depend on any internal packages.

To run tests:

    python setup.py test

 Alternatively, you can use Nose directly:

 	python setup.py develop
    nosetests tests/

To install a local copy of the code in to a virtual environment (for testing
changes to PyLCP in your LCP App project):

    python setup.py develop

Contributing to PyLCP
---------------------
If you have an idea to make this library more useful for other LCP App developers, we
welcome your contributions. Here is a rough guide for a process to follow:

1. Fork the repo <https://github.com/Points/PyLCP> in to your GitHub account.

1. Talk through your idea with a member of the platform team. They'll have
ideas on how to make your feature fit with the LCP architecture and have
applicability to the broadest set of app developers.

1. Implement your changes, commit, and push to your fork of the repo. Be sure the
tests run cleanly.

1. Create a pull request.

1. Address any concerns identified during the review of the pull request.
