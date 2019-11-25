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
:summary: Defines a Partial Class to group Project (RST & API) common logic
"""
import os
import abc
import logging

from doctool import settings
from doctool.helpers import Types
from doctool.helpers import ProjectHelper

from doctool.interfaces import IProject
from doctool.interfaces import IManager

logger = logging.getLogger(__name__)


class PartialProject(IProject):
    """
    Partial Project Class

    Abstract methods:

        * setup : Must be implemented to treat all prerequisites.
        * build : Must be implemented to execute building process.
        * teardown : Must be implemented to ensure all execution process remains clean.

    Methods:

        * __getattribute__ : Append logical repo path to relative path stored in the configuration file, if so.

    Properties:

        * configuration : The global configuration dict read from the configuration file by the Manager Class.
        * id : The Unique Identifier for the project.
        * rank : The rank of the project if Mode MULTIPLE *
        * toctree : The project global "Table Of Content Tree" reference
        * manager : The Manager instance
        * helper : The Helper instance **
        * src_dirname : The Project source directory path ***
        * out_dirname : The final output directory path held by the Manager Class
        * data : A selection of data used for writing project's specification (conf.py)
            and running the underlying engine, Sphinx

    * : The ranking is active only if more than one project is to be built.
    ** : The Helper instance is either a ProjectHelper or a CodeProjectHelper instance.
    *** : The building process is done in a temporary folder not the real source directory path.
    """

    __metaclass__ = abc.ABCMeta

    def __getattribute__(self, attr):
        """
        Override.

        By applying a naming convention to some attributes, those would be automatically concatenated to
        The Documentation Base Source Directory.

        :param attr: The Attribute name to be looked up in the __dict__ instance.
        :type attr: str

        :return: The Associated value
        :rtype: object
        """
        returned = None
        default = super(IProject, self).__getattribute__(attr)
        if attr.startswith('_dir'):
            possible_path = self.helper.absjoin(settings.REPO_BASE, default)
            if os.path.exists(possible_path):
                returned = possible_path
            else:
                returned = default
        # FIXME: Seems not to be used anymore?!
        # elif attr.startswith('_set'):
        #     returned = set()
        #     for p in attr:
        #         possible_path = self.helper.absjoin(settings.REPO_BASE, p)
        #         if os.path.exists(possible_path):
        #             returned.add(possible_path)
        #         else:
        #             returned.add(p)
        return returned or default

    def __str__(self):
        string = u''
        for attr, value in self.__dict__.items():
            if not attr.startswith('__'):
                string += u'{0} : {1}\n'.format(attr, value)
        return string

    __repr__ = __str__

    def __init__(self, manager, configuration):
        """
        Constructor

        :param manager: The ProjectManager instance
        :type manager: ProjectManager

        :param configuration: The Project Configuration data
        :type configuration: dict
        """
        # Asserting we passe a Manager instance which respect the Interface Contract
        assert issubclass(manager.__class__, IManager), ("You must pass in a derived Class instance "
                                                         "from IManager Interface")
        # Keeping a reference on the Manager instance.
        self._manager = manager
        # The project Configuration dictionary
        # self._configuration = Types.AttributeDict(configuration)
        self._configuration = self.load(configuration)

        # The project is the home page and it should appear in the navigation bar)?
        self.nav = self._configuration.get('nav', False)
        # The project is the home page?
        self.home = self._configuration.get('home', False)
        # Allow to display or hide left/right menu
        self.menu = self._configuration.get('menu', {"left": True, "right": True})
        # Is this project included in the search bar
        self.search = self._configuration.get('search', True)
        # The maximum depth for Toc tree recursion (default to 3)
        # lower-cased `maxdepth` is the project-level key, whereas upper-cased one is the global-level.
        self._maxdepth = self._configuration.get('maxdepth', self._configuration.get('MAXDEPTH', 3))

        # Optional project's icon
        self.icon = self._configuration.get('icon')
        # Optional project's layout
        # Possible values:
        #   - 3-columns
        #   - 2-columns-left
        #   - 2-columns-right
        self.layout = self._configuration.get('layout')

        # The project Unique Identifier
        self._uid = self._configuration.get('id', self._default_uid)
        # The project's name (from Configuration file)
        self._name = self._configuration.name
        # The project output format {HTML, PDF, WORD, ...} received from the Commandline
        self._output_format = manager.output_format
        # The project Ranking index
        self._rank = self._configuration.rank
        # The project source directory
        self._dir_source = self._configuration.dir2parse
        # The Project's extra paths to be appended to the module `sys.path`
        extra_paths = []
        for path in self._configuration.get('extra_sys_paths') or []:
            if not os.path.isabs(path):
                path = ProjectHelper.absjoin(self._dir_source, path)
            if os.path.exists(path):
                extra_paths.append(path)
            else:
                logger.warning('Extra sys path %s does not exist!', path)

        self._extra_paths = extra_paths
        # The Project's metadata (theme, title, copyright, ...
        self._metadata = self._configuration.metadata
        # The Project's Type
        self._is_api = self._configuration.api
        # The Project's suffix for ReSt file(s) {rst|rest|...}
        self._suffix = self._configuration.get('suffix', 'rst')
        # The Project's suffix for ReSt file(s) {rst|rest|...}
        self._override = self._configuration.get('override', True)
        # The Project TOC tree mapping
        self._toctree = None
        # The Project TOC first valid link
        self._first_link = ""

        # Public attribute for Theme Support
        self.theme = manager.theme

    @property
    def _default_uid(self):
        """
        Property computing based on path to parse
        the Project's UID

        :rtype: str
        :return: The project's UID
        """
        dir2parse = self.helper.normpath(
            self._configuration.dir2parse
        ).replace('/', ' ').strip()
        return self.helper.slugify(dir2parse)

    @property
    def configuration(self):
        """
        Holds the project's configuration Types.AttributeDict

        :return: the project's configuration
        :rtype: Types.AttributeDict
        """
        return self._configuration

    @property
    def dryrun(self):
        """
        If set the whole process is run without any physical action on the disk

        :return: Whether or not the process must be run "dry" or not
        :rtype: bool
        """
        return self._configuration.get('dry_run', False)

    @property
    def maxdepth(self):
        """
        The maximum depth for Toc tree recursion (default to 3)

        :rtype: int
        :return: maximum depth
        """
        return self._maxdepth

    @property
    def is_api(self):
        """
        Holds the project's type

        :return: Whether or not the project is of API type
        :rtype: bool
        """
        return self._is_api

    @property
    def name(self):
        """
        Holds the project's Name string

        :return: the project's Name string
        :rtype: str
        """
        return self._name

    @property
    def slug(self):
        """
        Holds the project's Name string as a slug

        :return: the project's Name' Slug string
        :rtype: str
        """
        return self.helper.slugify(self.name)

    @property
    def id(self):
        """
        Holds the project's UID string

        :return: the project's UID string
        :rtype: str
        """
        return self._uid

    @property
    def suffix(self):
        """
        Holds the project's for ReSt file(s) extension

        :return: the project's ReSt file(s) extension
        :rtype: str
        """
        return self._suffix

    @property
    def override(self):
        """
        Holds whether project's generation file(s) must be override or not

        :return: the project's override condition
        :rtype: bool
        """
        return self._override

    @property
    def rank(self):
        """
        Holds the project's Rank integer

        :return: the project's Rank integer
        :rtype: int
        """
        return self._rank

    @property
    def extra_paths(self):
        """
        Holds the Project's Extra Paths to be appended to the `sys.path` module

        :return: the project's Extra Paths
        :rtype: list
        """
        return self._extra_paths

    @property
    def metadata(self):
        """
        Holds the project's Metadata

        :return: the project's Metadata
        :rtype: Types.AttributeDict
        """
        return Types.AttributeDict(self._metadata)

    @property
    def toctree(self):
        """
        Holds the project's Table of contents (TOC) tree

        :return: A dictionary containing all mapped links and
            its associated values tuple(abspath, relpath)
        :rtype: Types.AttributeDict
        """
        return self._toctree

    @property
    def first_link(self):
        """
        Holds the project's TOC tree first valid link

        :return: the project's TOC tree first valid link
        :rtype: str
        """
        return self._first_link

    @property
    def manager(self):
        """
        Wraps Main Manager instance into a clearer self property if needed

        :return: IManager subclass instance
        :rtype: ProjectManager
        """
        return self._manager

    @property
    def helper(self):
        """
        Wraps Main Manager Helper instance into a clearer self property if needed

        :return: ProjectHelper instance
        """
        return self._manager.helper

    @property
    def src_dirname(self):
        """
        Abstract property

        Should implement a way to retrieve the project's source dirname

        :return: The Project's source dirname
        :rtype: str
        """
        assert os.path.exists(self._dir_source), "The Base directory does NOT exists ! ({0})".format(self._dir_source)
        assert os.path.isdir(self._dir_source), "The Base directory is NOT a directory ! ({0})".format(self._dir_source)

        return self.helper.normpath(self._dir_source)

    @property
    def data(self):
        """
        Export this instance as a dictionary

        :return: Self as a dictionary minus some non-useful attributes
        :rtype: Types.AttributeDict
        """
        return self.manager.data_context_builder(
            uid=self.id,
            project_name=self.name,
            master_doc='index',
            output_dir=self.helper.absjoin(self.manager.output_dir, self.id),
            source_dir=self.src_dirname,
            output_format=self._output_format,
            extra_paths=self.extra_paths,
            metadata=self.metadata,
            theme=self.theme
        )

    @property
    def conf_filename(self):
        """
        Property holding the Configuration filename
        Typically the `conf.py` for Sphinx

        :return: The Configuration filename
        :rtype: str or unicode
        """
        return self.helper.absjoin(self.src_dirname, 'conf.py')

    def build_toctree(self, source_dir):
        """
        Builds the Project's Toctree according the context

        :param source_dir: The source directory
        """
        self._toctree = []
        index = self.helper.absjoin(source_dir, 'index.rst')
        if os.path.isfile(index):
            with open(index, 'r') as handle:
                index_lines = handle.readlines()
            toctree = Types.TOCList(
                index_lines,
                maxdepth=self.maxdepth,
                src_dirname=source_dir,
                suffix=self.id
            )
            self._toctree = toctree.build().items
            self._first_link = toctree.first_link

    @classmethod
    def load(cls, configuration):
        """
        Loads from filesystem the configuration file into memory.

        :param configuration: The Configuration minimal data got from the global Configuration file.
        :type configuration: dict

        :return: The configuration data
        :rtype: Types.AttributeDict
        """
        return ProjectHelper.load_from_file(configuration)

    @abc.abstractmethod
    def setup(self):
        """
        Abstract Method

        The building process
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

        The building process
        """
