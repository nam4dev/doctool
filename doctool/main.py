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
The DocTool Project aims at providing an easy-to-use overlayer of Sphinx to build
Multiple Projects into one with a clear, user-friendly template (Android-like).

**Usage :**

    * **-l --list-projects**: Use this option to get an exhaustive list of known projects from your Configuration file.

    * **-s, --simple**: Use this option to provide either a key from your Configuration file
        or a directory path containing ReSt files.

    * **-b, --build**: Use this option to provide either a combination of keys from your Configuration file
        or a combination of directories path containing ReSt files.
        
    * **-v, --version**: Use this option to provide the version of documentation to be build (used for multi-version docmentation).

    * **-o, --output**: Use this option to provide output directory path where your documentation is to be generated.

    * **-c, --conf-file**: Use this option to provide the configuration file path.

    * **-t, --title**: Use this option to provide the title to your whole generated documentation as a string.

    * **-tn, --theme-name**: Use this option to provide the Theme name
        to your whole generated documentation as a string.

        Available Theme(s) :

            #. bootstrap

    * **-i, --interactive**: Use this option to get interactive mode.

For more details get yourself posted about this tool at::

    `Github - Doctool - Auto Documentation Aggregator <https://github.com/nam4dev/doctool>`_
"""
import os
import sys
import logging
import argparse

DOCTOOL_ROOTDIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.insert(0, DOCTOOL_ROOTDIR)

from doctool import settings
from doctool.managers import ProjectManager


def make_parser(description=__doc__):
    """
    Makes a parser using the module :mod:`argparse.ArgumentParser`

    :param description: the parser description
    :type description: str

    :rtype: argparse.ArgumentParser
    :return: ArgumentParser instance
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-l", "--list-projects",
                        action="store_true",
                        dest="list_projects",
                        help="Use this option to get an exhaustive list of "
                             "known projects from your Configuration file.")

    parser.add_argument("-o", "--output-dir",
                        type=str,
                        action="store",
                        dest="output",
                        help="Use this option to provide output directory path "
                             "where your documentation is to be generated.")

    parser.add_argument("-v", "--version",
                        type=str,
                        action="store",
                        dest="version",
                        help="Use this option to provide the version of documentation "
                             "to be build (used for multi-version docmentation)")

    parser.add_argument("-c", "--conf-file",
                        type=str,
                        action="store",
                        dest="conf_file",
                        help="Use this option to provide the configuration file path.",
                        default="")

    parser.add_argument("-t", "--master-title",
                        type=str,
                        dest="master_title",
                        default="",
                        help="Use this option to provide the title to your whole generated documentation as a string.")

    parser.add_argument("-tn", "--theme-name",
                        type=str,
                        dest="theme_name",
                        default="bootstrap",
                        help="Use this option to provide the theme name "
                             "to your whole generated documentation as a string.")

    parser.add_argument("-i", "--interactive",
                        type=int,
                        dest="interactive",
                        default=0,
                        help="Use this option to get interactive mode.")

    projects_group = parser.add_argument_group('Doctool Build Modes',
                                               '''SIMPLE : Match Sphinx behavior building from a single project source.
                                               MULTIPLE : Aggregate more than 1 project source together.''')

    projects_group.add_argument("-b", "--build",
                                dest="projects",
                                default=[],
                                nargs='*',
                                help="Use this option to provide either a combination "
                                     "of keys from your Configuration file "
                                     "or a combination of directories path containing ReSt files.")

    return parser


def main():
    """
    DocTool Entry point

    :rtype: int
    :return: Execution status
    """
    parser_ = make_parser()
    namespace = parser_.parse_args(sys.argv[1:])
    exit_status = 0

    if not (namespace.projects or namespace.list_projects):
        parser_.print_help()
    else:
        # for performance, I do not use :func:`vars` builtin function
        manager = ProjectManager(**namespace.__dict__)
        log_level = settings.DOCTOOL_GLOBAL_LOGGING_LEVELS.get(
            manager.global_conf.LOG_LEVEL,
            settings.DOCTOOL_GLOBAL_LOGGING_LEVEL
        )
        logging.basicConfig(level=log_level)

        exit_status = manager.run()

    sys.exit(exit_status)


if __name__ == '__main__':
    main()
