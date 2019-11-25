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
from distutils.core import setup
from setuptools import find_packages

import doctool


setup(
    name=doctool.__name__,
    version=doctool.__version__,
    packages=find_packages(),
    url=doctool.__url__,
    license=doctool.__copyright__,
    author=doctool.__author__,
    author_email=doctool.__author_email__,
    description=doctool.__description__,
    requires=doctool.__requires__,
    entry_points={
        'console_scripts': [
            'doctool = doctool.main:main'
        ]
    },
    include_package_data=True
)
