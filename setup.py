# Necessary to supress on error in Python 2.7.3 at the completion of
# python setup.py test.
# See http://bugs.python.org/issue15881#msg170215
import multiprocessing        # NOQA

import distutils.command.clean
import os
import pkg_resources
import setuptools
import subprocess


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


def read_requirements(file_path):
    return [
        i.strip()
        for i in pkg_resources.resource_string(__name__, file_path).split()
        if i.strip()[0:1] != '#' and i.strip()[0:2] != '--' and len(i.strip()) > 0
    ]


REQUIREMENTS = read_requirements('requirements.txt')
TEST_REQUIREMENTS = read_requirements('requirements-dev.txt')


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
                 tests_require=TEST_REQUIREMENTS,
                 cmdclass={
                     'clean': Clean
                 },
                 )
