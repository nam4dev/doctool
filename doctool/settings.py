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
:summary: Groups all Project's Constants
"""
import os
import sys
import logging


def normpath(p):
    """
    Norm a path as Unix-like separator

    :type p: str
    :param p: The path

    :rtype: str
    :return: The normed path
    """
    return os.path.abspath(p).replace('\\', '/')


def absjoin(*args):
    """
    Custom join + abspath

    .. note:: :meth:`os.path.abspath` method calls :meth:`os.path.normpath` method. Therefore, there's no need to
        call it after the absjoin method.

    :param args: Non Keyword arguments to be joined together

    :rtype: str
    :return: An absolute & normed joined path
    """
    return normpath(os.path.join(*args))


__ROOTDIR__ = normpath(os.path.dirname(__file__))
__OUTPUT_DIRNAME__ = 'doctool_builds'

IS_WINDOWS = sys.platform == 'win32'

LOGICAL_JAVA_BIN_PATH = r'C:/windows/system32/java.exe' if IS_WINDOWS else '/usr/bin/java'

DOCTOOL_ROOTDIR = absjoin(__ROOTDIR__, '..')
TEMPLATES_DIR = absjoin(__ROOTDIR__, '_templates')

DEFAULT_HOST = '(127.0.0.1|localhost)'
DEFAULT_VERSION = '0.0.0.0'

# Little default specific variable
REPO_BASE = absjoin(DOCTOOL_ROOTDIR, '..')

# REPO = absjoin(REPO_BASE, 'avt')
DOCUMENTATION_REPO = absjoin(REPO_BASE, 'documentation')

DEFAULT_CONFIG = absjoin(DOCUMENTATION_REPO, 'doctool_settings.json')
DEFAULT_OUTPUT_DIRNAME = absjoin(DOCUMENTATION_REPO, __OUTPUT_DIRNAME__)
DEFAULT_OUTPUT_LOG_FILENAME = absjoin(DEFAULT_OUTPUT_DIRNAME, 'doctool_logs.txt')

DOCTOOL_GLOBAL_LOGGING_LEVEL = logging.DEBUG
DOCTOOL_GLOBAL_LOGGING_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL,
}
