Python Client Library for the Points Loyalty Commerce Platform
==============================================================

This library provides a simple interface for submitting signed 
requests to the 
`Points Loyalty Commerce Platform <http://points.github.io/Loyalty-Commerce-Platform/>`_
(LCP):

Quick Start
-----------

Install PyLCP from PyPI::

    pip install pylcp

If you use the pylcp.testing module to test your apps built with PyLCP, you
will need to install the `Nose <http://nose.readthedocs.org/en/latest/>`_ unit testing framework.

.. code-block:: bash

    pip install nose

This is not installed with the run-time requirements since Nose is typically
only used for testing. We don't want to require it to be installed in your
production virtual environment.

The example below shows how to submit a signed request to the LCP::

    $ python
    Python 2.7.9 (default, Dec 12 2014, 14:33:46)
    [GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.56)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from pylcp.api import Client
    >>> client = Client(
    ... 'https://lcp.points.com/v1',
    ... key_id='my_mac_key_identifier',
    ... shared_secret='my_mac_key'
    ... )
    >>> response = client.get('/accounts/my_account_id')

User's Guide
------------
.. toctree::
    :maxdepth: 2

    api
    testing

Contributer Guide
-----------------
.. toctree::
    :maxdepth: 1

    dev

References
----------
For further information on the Loyalty Commerce Platform, check out 
the `Getting Started Guide <http://points.github.io/Loyalty-Commerce-Platform/index.html>`__.

The PyLCP library uses the `Requests <http://www.python-requests.org/en/latest/>`__
library for sending HTTP requests to the
LCP. In particular, responses are instances of the 
`requests.Response <http://docs.python-requests.org/en/latest/api/#requests.Response>`__ class.

:ref:`genindex`
:ref:`search`

