======
Readme
======

Purpose
-------

This library provides a simple interface for submitting signed and unsigned
requests to the Points Loyalty Commerce Platform (LCP).

Features
--------

* The LCP API implemented as a `JSON Schema <http://json-schema.org/> `_ (mv, credit & debit only).
* An LCP client that validates all requests against the JSON schema.


Running from the Package
------------------------

The |lib-full-name| can be installed from a requirements file by adding the
following lines:

.. code-block:: text

	--index-url=http://ops-build2.points.com:8000/pypi/PyLCP

and then running ``pip install``.

Alternatively, the package file can be downloaded from the TeamCity build.

    http://prod-builds-1.points.com:8111/project.html?projectId=Development_DevPyLCP&tab=projectOverview

.. warning::
    The |lib-full-name| is meant to be configured. More information on :doc:`configuration`

Running from Source
-------------------

If you wish to develop the |lib-full-name| code at the same time as your client application, follow these steps to link
the library code.

#. Create a virtual environment for your application project
#. Install the |lib-full-name| requirements (see below) in this environment.

You can now edit code in either project, with the changes immediately reflected. No additional steps are necessary to
pick up changes made in the library source code.

To test modifications to the dist locally, it is possible to spin up a web server and host the package there. Paver
tasks exist to do this work:

.. code-block:: text

    paver package && paver host_local

To reference this location in another project, modify its requirements file to include:

.. code-block:: text

    --extra-index-url=http://127.0.0.1:9000/dist

Alternatively, it is possible to install the package manually:

.. code-block:: text

    pip install --extra-index-url=http://127.0.0.1:9000/dist PyLCP

Requirements Files
------------------

There are two requirements files in the `requirements` directory.

- base.txt - This is maintained by setuptools and contains all the pre-requisites for the |lib-full-name|. If using the
  library from the package container from the package, these dependencies will be automatically installed in your
  environment. If running from source, you must install these packages e.g. `pip install -r requirements/base.txt`.
- development.txt - Additional packages required for development including Coverage and Paver.  Also includes packages
  required for generating the online documentation, including Pygments and Sphinx.

Tests
-----

All new code must be tested with automated unit tests. Unit tests can be executed by running `paver unit_tests`.

Other Documentation
-------------------

Read the :doc:`examples` for integrating the |lib-full-name| into your testing setup.
