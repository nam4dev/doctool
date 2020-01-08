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
:summary: Groups all Project's Interfaces

Available Interfaces :

    * IBuilder
    * IProject
    * IManager
"""
import abc


class _ICommon(object):
    """
    Protected Common Interface for Abstract Methods :

        * setup : Must be implemented to treat all prerequisites.
        * build : Must be implemented to execute building process.
        * teardown : Must be implemented to ensure all execution process remains clean.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def setup(self):
        """
        Abstract Method

        The setup process
        """

    @abc.abstractmethod
    def build(self):
        """
        Abstract Method

        The building process
        """

    @abc.abstractmethod
    def teardown(self):
        """
        Abstract Method

        The teardown process
        """


class IBuilder(object):
    """
    Defines a Interface for Builder Sub-classes
    """

    __metaclass__ = abc.ABCMeta

    class Status(object):
        """
        Inner Status Class - Acts as an enum
        """
        UNKNOWN = -2
        FAILURE = -1
        SUCCESS = 0

    @property
    @abc.abstractmethod
    def build_info(self):
        """
        Property holding the build information

        :rtype: dict
        :return: The Build information as dictionary
        """

    @abc.abstractmethod
    def build(self, projects=None):
        """
        Defines the Build process.

        :param projects: A collection of project instances (IProject sub-class)
        :type projects: tuple or list

        :return: The build status
        :rtype: IBuilder.Status

            * IBuilder.Status.UNKNOWN: -2
            * IBuilder.Status.FAILURE: -1
            * IBuilder.Status.SUCCESS: 0
        """


class IProject(_ICommon):
    """
    Interface for Project

    Abstract Methods :

        * setup : Must be implemented to treat all prerequisites.
        * build : Must be implemented to execute building process.
        * teardown : Must be implemented to ensure all execution process remains clean.
    """


class IManager(_ICommon):
    """
    Interface for Manager

    Abstract Methods :

        * setup : Must be implemented to treat all prerequisites.
        * build : Must be implemented to execute building process.
        * teardown : Must be implemented to ensure all execution process remains clean.
        * run : Must be implemented to ensure the whole execution process.

    Abstract Properties :

        * helper: An helper instance in charge of delegating common tasks
        * output_dir: The output directory where documentation shall be generated
    """

    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def helper(self):
        """
        Abstract property

        Should implement a way to get an Helper instance if needed or None.

        :return: An helper instance or None
        :rtype: object or None
        """

    @property
    @abc.abstractmethod
    def output_dir(self):
        """
        Abstract property

        Should implement a way to get a valid output path.

        :return: A valid output path
        :rtype: str or unicode
        """

    @abc.abstractmethod
    def run(self):
        """
        Abstract Method

        The whole process run
        """
