# -*- coding: utf-8 -*-
#
# This file is execfile()d with the current directory set to its
# containing dir.

import datetime
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

import pylcp    # noqa

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'PyLCP'
copyright = u'2012-{0}, Points International Ltd.'.format(datetime.datetime.now().year)

with open('../../version_number.txt', 'r') as f:
    version = f.readline()
release = version

exclude_patterns = []
pygments_style = 'sphinx'

html_theme = 'alabaster'
html_static_path = ['_static']
htmlhelp_basename = 'PyLCPdoc'

intersphinx_mapping = {
    'python': ('http://docs.python.org/2.7', None),
    'requests': ('http://docs.python-requests.org/en/latest/', None),
}
