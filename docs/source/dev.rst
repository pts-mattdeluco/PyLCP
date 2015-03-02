.. _dev:

How to Help
-----------

PyLCP and the LCP itself are under active development, and contributions are more than welcome!

#. Check for open issues or open a fresh issue to start a discussion around a bug.
#. Fork `the repository <https://github.com/points/pylcp>`_ on GitHub and start making your
   changes to a new branch.
#. Write a test which shows that the bug was fixed.
#. Send us a pull request.

We use the `coverage <http://nedbatchelder.com/code/coverage/>`_ package to measure 
code coverage and `Sphinx <http://sphinx-doc.org/>`_ to generate documentation. 
Make sure any pull requests that you submit include appropriate test coverage and
documentation updates.

Development Dependencies
------------------------

To run tests on PyLCP, install the development requirements from requirements-dev.txt
which also install the run-time requirement::

    pip install -r requirements-dev.txt

Testing
-------

To run tests::

    nosetests tests/

To install a local copy of the code in to a virtual environment (for testing
changes to PyLCP in your LCP App project), run the following with your app's
virtualenv active::

    python setup.py develop

or if you prefer pip::

    pip install -e path/to/pylcp/source

Documentation
-------------

To build build the documentation, install Sphinx and related requirements::

    cd docs
    pip install -r requirements.txt
    make html

To view locally built documentation, open the file docs/build/html/index.html in
a browser.
