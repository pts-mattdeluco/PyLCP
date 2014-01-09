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

Developer Notes
---------------
We want to eventually open source this package on Github. We would
like to keep the footprint small and use tools for building and testing that
will be familiar to most Python developers. Hence PyLCP is built minimally
using setuptools and does not depend on any internal packages.

To run tests:

    python setup.py test

 Alternatively, you can use Nose:

    nosetests tests/

To install a local copy of the code in to a virtual environment (for testing
changes to PyLCP in your LCP App project):

    python setup.py develop

Contributing to PyLCP
---------------------
Several teams at Points are using PyLCP to build platform apps. If you have
an idea to make this library more useful for other LCP App developers, we
welcome your contributions. Here is a rough guide for a process to follow:

1 - Talk through your idea with a member of the platform team. They'll have
ideas on how to make your feature fit with the LCP architecture and have
applicability to the broadest set of app developers.

2 - Implement your changes on the dev_head branch. Commit, push and ensure you
have a clean build on TeamCity: https://prod-builds-1.points.com:8112/viewType.html?buildTypeId=Development_DevPyLCP_PyLCP

3 - Create a code review in the PyLCP project on Crucible. In addition to
members of the Platform team, ensure that other interested developers at
Points are included to gain feedback.

4 - Address any concerns identified, adding additional commits to the review
as follow-up.

5 - Once the code is done, increment the version number in version_number.txt
and commit this change. As a rule, push all commits except version_number.txt
in order to ensure a clean build. As a final step, edit, commit and push the
change to version_number.txt to trigger the TeamCity build that deploys the
new package to our internal PyPI server.
