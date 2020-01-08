#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Namgyal BRISSON (nam4dev)"
__since__ = "10/25/2019"
__copyright__ = """MIT License

Copyright (c) 2019 Namgyal Brisson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
:summary: Defines all what is required to build Doctool as a python package.

.. note:: Run this script with `build` or `install` mode according your needs.
    A Wheel can be generated via `bdist_wheel` option in `build` mode.

.. important:: When installed, a command-line alias, named **doctool** is created !
    Therefore calling simply **doctool** is enough.
"""
import os
import sys

from distutils.core import setup
from setuptools import find_packages

__ROOTDIR__ = os.path.dirname(
    os.path.abspath(__file__)
)
DOCTOOL_ROOTDIR = __ROOTDIR__
sys.path.insert(0, DOCTOOL_ROOTDIR)

__version__ = '0.9.2.0'
__author_email__ = 'namat4css@gmail.com'
__description__ = """\
Doctool is written in python overlaying Sphinx \
to enable multiple Sphinx projects to be aggregated into a single web application.
Multiple versions can be easily handled as well by this tool.
Doctool is able to automatically handle one's code source, in order to generate API documentation."""

with open(os.path.join(__ROOTDIR__, 'requirements.txt')) as fd:
    __requires__ = [req.strip() for req in fd.readlines() if req]

with open(os.path.join(__ROOTDIR__, 'README.md')) as fd:
    __long_description__ = fd.read()

__url__ = 'https://github.com/nam4dev/doctool'


setup(
    name='doctool',
    version=__version__,
    packages=find_packages(),
    url=__url__,
    license=__copyright__,
    author=__author__,
    author_email=__author_email__,
    description=__description__,
    long_description=__long_description__,
    requires=__requires__,
    entry_points={
        'console_scripts': [
            'doctool = doctool.main:main'
        ]
    },
    include_package_data=True
)
