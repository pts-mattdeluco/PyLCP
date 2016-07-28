# Necessary to supress on error in Python 2.7.3 at the completion of
# python setup.py test.
# See http://bugs.python.org/issue15881#msg170215
import multiprocessing  # NOQA

import distutils.command.clean
import os
import setuptools
import subprocess

REQUIREMENTS = [
    'future>=0.4.13,<1.0',
    'requests>=2.2.1,<3.0',
    'simplejson>=3.6.4'
]
DEV_REQUIREMENTS = [
    'coverage==4.2',
    'flake8<3.0.0',
    'mccabe==0.5.1',
    'mock==2.0.0',
    'nose==1.3.7',
    'pep8==1.7.0',
    'pyflakes==1.2.3',
    'teamcity-messages==1.19'
]
DOCS_REQUIREMENTS = ['sphinx']


class Clean(distutils.command.clean.clean):
    def run(self):
        subprocess.call('find . -name *.pyc -delete'.split(' '))
        subprocess.call('rm -rf *.egg/ test_results/ .coverage .noseids'.split(' '))
        distutils.command.clean.clean.run(self)


def read_file(file_name):
    """Utility function to read a file."""
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


def read_first_line(file_name):
    """Read the first line from the specified file."""
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.readline().strip()


setuptools.setup(name='PyLCP',
                 version=read_first_line('version_number.txt'),
                 description="Python client library for Points Loyalty Commerce Platform.",
                 long_description=read_file('README.md'),
                 classifiers=[
                     'Development Status :: 5 - Production/Stable',
                     'Environment :: Web Environment',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: BSD License',
                     'Natural Language :: English',
                     'Operating System :: POSIX :: Linux',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3.3',
                     'Programming Language :: Python :: 3.4',
                     'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                     'Topic :: Software Development :: Libraries :: Python Modules'
                 ],
                 keywords='LCP REST',
                 author='Points International',
                 author_email='',
                 url='',
                 license='',
                 packages=setuptools.find_packages(exclude=['tests']),
                 include_package_data=True,
                 zip_safe=False,
                 install_requires=REQUIREMENTS,
                 entry_points="""
                 # -*- Entry points: -*-
                 """,
                 test_suite='nose.collector',
                 tests_require=DEV_REQUIREMENTS,
                 extras_require={
                     'dev': DEV_REQUIREMENTS,
                     'docs': DEV_REQUIREMENTS + DOCS_REQUIREMENTS
                 },
                 cmdclass={
                     'clean': Clean
                 },
                 )
