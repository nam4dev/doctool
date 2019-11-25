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
:summary: Groups all Project's Model Classes
"""
import re
import os
import time
import logging
import tempfile

from doctool.helpers import Types
from doctool.helpers import ProjectHelper

from doctool.partials import PartialProject

logger = logging.getLogger(__name__)


class Theme(object):
    """
    Implements Theme data
    """

    def __init__(self, **kwargs):
        """
        Constructor

        Set all given keyword arguments as its own attributes
        """
        for attr, value in kwargs.items():
            setattr(self, attr, value)


class RSTProject(PartialProject):
    """
    This kind of project handles only RST format
    """

    def setup(self):
        """
        Parsing RST index to get the Project's structure
        """

    def build(self):
        """
        Method building the doc tree
        """
        self.build_toctree(self.src_dirname)

    def teardown(self):
        """
        Cleaning all what need to be cleaned
        """
        self.manager.garbage.append(self.conf_filename)


class CodeProject(RSTProject):
    """
    This kind of project handles only Code format (*.py)
    """

    __INIT__ = '__init__.py'
    EXCLUDED_MODULES_DEFAULT = {
        '^test.*',
        '^build.*'
    }

    API_OPTIONS = [
        'members',
        'undoc-members',
        'show-inheritance',
        'private-members',
        ('exclude-members', ('__dict__', '__weakref__', '__repr__', '__module__')),
        'special-members',
    ]
    HEADING_LEVELS = ['=', '-', '~', ]

    @classmethod
    def format_heading(cls, level, text, anchor=0):
        """
        Create a heading of <level> [1, 2 or 3 supported].

        :param anchor:
        :param level: Heading level.
        :param text: Content to be written
        """
        lf = '\n'
        anchor_txt = ''
        underlining = cls.HEADING_LEVELS[level - 1] * len(text)
        if anchor and level == 1:
            anchor_txt += '.. _{0}: {1}{1}'.format(text, lf)
        return '{3}{0}{2}{1}{2}{2}'.format(text, underlining, lf, anchor_txt)

    @staticmethod
    def skip(module):
        """
        Check if we want to skip this module.

        :param module: Module name to be skipped
        """
        # skip it, if there is nothing
        # (or just \n or \r\n) in the file
        return os.path.getsize(module) < 3

    @staticmethod
    def makename(package, module, **opts):
        """
        Join package and module with a dot.

        :param opts: a sequence substitution to apply to name

        :param package: python package
        :type package: str

        :param module: python module
        :type module: str
        """
        # Both package and module can be None/empty.
        if package:
            name = package
            if module:
                name += '.' + module
        else:
            name = module

        sub = opts.get('sub', "")
        if sub:
            name = name.replace(sub, "").strip()

        if not opts.get('writing', 0):
            name = name or ""

        if name.startswith('.'):
            name = name[1:]

        return name

    def __init__(self, manager, configuration):
        """
        Constructor

        :param manager: The manager instance
        :param configuration: The configuration instance
        """
        super(CodeProject, self).__init__(manager, configuration)

        self._current_package = None
        self.indices_and_tables = False
        self._output_dir = ""
        self._api_toc = []
        self._api_toctree = []

        self._excluded_modules = CodeProject.EXCLUDED_MODULES_DEFAULT.copy()
        self._notoc = self.configuration.get('notoc', False)
        self._master_doc = self.configuration.get('master_doc', 'index')
        self._excluded_modules.update(self.configuration.get('excluded_modules', {}))

        self._excluded_modules = {re.compile(exclude) for exclude in self._excluded_modules}

        self._filtered_packages = self.configuration.get('filtered_packages', {})
        self._dev_mode_src_root = self.configuration.get('dev_mode_src_root', "")

    @property
    def api_toctree(self):
        """
        Holds the API project analysis sorted toctree

        :rtype: list
        :return: The API project analysis sorted toctree
        """
        if not self._api_toctree and self._api_toc:
            self._api_toc.sort()
            self._api_toctree = []
            for name in self._api_toc:
                self._api_toctree.append(name.replace('.', '/'))

        return self._api_toctree

    @property
    def notoc(self):
        """
        Holds whether a "Table of Content" has to be generated or not

        :rtype: bool
        :return: "Table of Content" has to be generated or not
        """
        return self._notoc

    @property
    def master_doc(self):
        """
        Holds the Project's Master Document Name

        .. note:: Generally, it is used for index(.html)

        :rtype: str
        :return: Project's Master Document Name
        """
        return self._master_doc

    @property
    def output_dir(self):
        """
        Holds the API project's ReSt output directory where all API analysis writes files

        .. note:: This directory is created in the system temporary folder via :mod:`tempfile`.

        :rtype: str or unicode
        :return: The ReSt output directory
        """
        return self._output_dir

    @property
    def data(self):
        """
        Export this instance as a dictionary

        :rtype: Types.AttributeDict
        :return: Self as a dictionary minus some non-useful attributes
        """
        data = super(CodeProject, self).data
        data.source_dir = self.output_dir
        data.dirs2append = [self.helper.absjoin(self.src_dirname, '..')]
        return data

    @property
    def api_options(self):
        """
        Property returning the API options
        from configuration or predefined default values

        :rtype: list
        :return: The API options
        """
        options = self.configuration.get('api_options', self.API_OPTIONS)
        return options

    def build_toctree(self, source_dir):
        """
        Builds the Project's Toctree according to the context

        :rtype: str
        :param source_dir: The source directory
        """
        self._toctree = []
        toctree = Types.TOCList(self.api_toctree,
                                is_api=True,
                                maxdepth=self.maxdepth,
                                src_dirname=source_dir,
                                suffix=self.id,
                                master_name=self.master_doc,
                                joined_stripped=True)
        self._toctree = toctree.build().items
        self._first_link = toctree.first_link

    def write_file(self, name, text, mode='wb'):
        """
        Write the output file for module/package <name>.

        :param mode: open mode
        :param name: Package or Module name.
        :param text: Content to be written.
        """
        if not name or self.dryrun:
            return
        filename = ProjectHelper.absjoin(self._output_dir, "{0}.{1}".format(name, self.suffix))
        ProjectHelper.write_file(filename, text, mode, self.override)

    def format_directive(self, module, package=None):
        """
        Create the automodule directive and add the options.

        :param module: Module name
        :param package: Package name
        """
        directive = '.. automodule:: {0}\n'.format(self.makename(package, module, sub=self._dev_mode_src_root))

        for option in self.api_options:
            if isinstance(option, (set, frozenset, tuple, list)) and len(option) > 1:
                directive += '\t:{}: {}\n'.format(option[0], ', '.join(option[1]))
            else:
                directive += '\t:{0}:\n'.format(option)
        return directive

    def create_module_file(self, package, module):
        """
        Build the text of the file and write the file.

        :param package: Package name
        :param module: Module name
        """
        text = self.format_heading(1, '{0} Module'.format(module))
        text += self.format_heading(2, ':mod:`{0}` Module'.format(module))
        text += self.format_directive(module, package)

        self.write_file(self.makename(package, module, writing=1, sub=self._dev_mode_src_root), text)

    def include_module(self, module):
        """
        Method evaluating whether the given module shall be included or not

        :param module: The module
        """
        if not self._current_package:
            included = 1
        else:
            included = 0
            logger.debug('Analysing module: {0}'.format(module))
            if module:
                for mod in self._current_package:
                    if mod in module:
                        logger.debug('Analysing module: {0} INCLUDED!'.format(module))
                        included = 1

        return included

    def include_package(self, root, master_package):
        """
        Defines whether or not the package should be included into analysis.

        :type root: str
        :param root: The root reference

        :type master_package: str
        :param master_package: The master package reference
        """
        if not self._filtered_packages:
            included = 1
        else:
            included = 0
            if not root or not master_package:
                logger.debug('Not enough data to process skipping!')
            else:
                parts, fullname_parts = ProjectHelper.split_all(root), []
                while parts:
                    el = parts.pop()
                    if el == master_package:
                        fullname_parts.append(el)
                        break
                    fullname_parts.append(el)

                fullname_parts.reverse()
                pkg_fullname = '.'.join(fullname_parts)

                current_pkg = self._filtered_packages.get(pkg_fullname)
                included = current_pkg is not None
                if included:
                    self._current_package = current_pkg
                    logger.debug('Package ``{0}`` included'.format(pkg_fullname))

        return included

    def create_package_file(self, root, master_package, subroot, py_files, subs):
        """
        Build the text of the file and write the file.

        :param root:
        :param master_package:
        :param subroot:
        :param py_files:
        :param subs:
        """
        package = os.path.split(root)[-1]
        text = self.format_heading(1, '{0} Package'.format(package))
        # add each package's module
        for py_file in py_files:
            if self.skip(os.path.join(root, py_file)) or (self._filtered_packages and
                                                       not self.include_package(root, master_package)):
                continue
            elif self.skip(os.path.join(root, py_file)) or self.is_excluded(package):
                continue

            is_package = py_file == self.__INIT__
            py_file = os.path.splitext(py_file)[0]
            py_path = self.makename(subroot, py_file, writing=1, sub=self._dev_mode_src_root)

            if not self.include_module(py_file):
                continue

            if is_package:
                heading = ':mod:`{0}` Package'.format(package)
            else:
                heading = ':mod:`{0}` Module'.format(py_file)
            text += self.format_heading(2, heading)
            text += self.format_directive(is_package and subroot or py_path, master_package)
            text += '\n'

        # build a list of directories that are packages (contains an INIT file)
        subs = [sub for sub in subs if os.path.isfile(os.path.join(root, sub, self.__INIT__))]

        # if there are some package directories, add a TOC for theses subpackages
        if subs:
            # text += self.format_heading(2, 'Subpackages')
            # text += '\n'
            # text += '.. toctree::\n'
            # text += '   :hidden:\n\n'
            for sub in subs:

                if self.is_excluded(sub) or not self.include_package(sub, master_package):
                    continue
                name = '{0}.{1}'.format(self.makename(master_package, subroot, writing=1,
                                                      sub=self._dev_mode_src_root), sub)
                # text += '   :mod:`{0}`\n'.format(name)
                if name not in self._api_toc:
                    self._api_toc.append(name)
            # text += '\n'

        self.write_file(self.makename(master_package, subroot, writing=1, sub=self._dev_mode_src_root), text, mode='w')

    def create_modules_toc_file(self, modules, name=None):
        """
        Create the module's index.

        :type modules: list or tuple
        :param modules: A sequence of module names

        :type name: str
        :param name: (Optional) The name
        """
        name, lf = name or self.master_doc, '\n'

        text = self.format_heading(1, '{0}'.format(self.name), anchor=1)
        text += '.. toctree::{0}'.format(lf)
        text += '   :maxdepth: {0}{1}{1}'.format(self.maxdepth, lf)

        modules.sort()
        prev_module = ''

        for module in modules:
            # look if the module is a
            # subpackage and, if yes, ignore it
            if module.startswith(prev_module + '.'):
                continue
            prev_module = module
            text += '   {0}{1}'.format(module, lf)

        if self.indices_and_tables:
            # Adding Indices and Tables directive.
            text += self.format_heading(1, 'Indices and tables', anchor=1)

            text += '{0}* :ref:`genindex`'.format(lf)
            text += '{0}* :ref:`modindex`{0}{0}'.format(lf)

        self.write_file(name, text, mode='w')

    def is_excluded(self, package):
        """
        Check if the directory is in the exclude list.

        :param package: The root path to be scanned
        """
        module_name = '.'.join([
            fragment
            for fragment in package.replace('\\', '/').replace(self.src_dirname, '').split('/')
            if fragment
        ])
        for exclude in self._excluded_modules:
            if exclude.search(module_name):
                logger.debug("Package ``{0}`` excluded from analysis".format(package))
                return 1
        return 0

    def load(self, configuration):
        """
        ** Override **

        Returns the configuration data as an AttributeDict

        :param configuration: The Configuration minimal data got from the global Configuration file.
        :type configuration: dict

        :return: The configuration data
        :rtype: Types.AttributeDict
        """
        return Types.AttributeDict(configuration)

    def setup(self):
        """
        Override

        Parsing Code source to generate RST file which reflects the API structure
        """
        super(CodeProject, self).setup()

        # use absolute path for root,
        # as relative paths like '../../foo' cause
        # 'if "/." in root ...' to filter out
        # *all* modules otherwise

        self._output_dir = tempfile.mkdtemp(str(time.time()).replace('.', '_'), 'doctoolAPI')
        pattern = re.compile(r'.*\.py$')

        # check if the base directory
        # is a package and get is name

        if self.__INIT__ in os.listdir(self.src_dirname):
            package_name = self.src_dirname.split('/')[-1]
        else:
            package_name = None

        toc = []
        for root, subs, filenames in os.walk(self.src_dirname, False):
            # keep only the Python script files
            py_files = sorted([f for f in filenames if pattern.match(f)])
            if self.__INIT__ in py_files:
                py_files.remove(self.__INIT__)
                py_files.insert(0, self.__INIT__)
                # remove hidden ('.') and private ('_') directories
            subs = sorted([sub for sub in subs if sub[0] not in ['.', '_']])

            # check if there are valid files to process
            if not py_files:
                continue
            if self.is_excluded(root):
                continue
            if not self.include_package(root, package_name):
                continue

            if self.__INIT__ in py_files:
                # we are in package ...
                if (subs or
                        # ... with subpackage(s)
                        len(py_files) > 1 or
                        # ... with some module(s)
                        # ... with a not-to-be-skipped INIT file
                        not self.skip(os.path.join(root, self.__INIT__))):
                    subroot = root[len(self.src_dirname):].lstrip(os.path.sep).replace(os.path.sep, '.')

                    self.create_package_file(root, package_name, subroot, py_files, subs)
                    name = self.makename(package_name, subroot, writing=1, sub=self._dev_mode_src_root).strip()

                    if name not in self._api_toc:
                        toc.append(name)
                        self._api_toc.append(name)

            elif root == self.src_dirname:
                # if we are at the root level,
                # we don't require it to be a package

                for py_file in py_files:
                    if not self.skip(os.path.join(self.src_dirname, py_file)):
                        module = os.path.splitext(py_file)[0]
                        self.create_module_file(package_name, module)
                        name = self.makename(package_name, module, writing=1, sub=self._dev_mode_src_root).strip()

                        if name not in self._api_toc:
                            toc.append(name)
                            self._api_toc.append(name)

        # create the module's index
        if not self.notoc:
            self.create_modules_toc_file(toc)

    def build(self):
        """
        Override

        Look for every file in the directory
        tree and create the corresponding ReST files.
        """
        self.build_toctree(self._output_dir)

    def teardown(self):
        """
        Override

        Cleaning all what need to be cleaned
            * The output directory
        """
        super(CodeProject, self).teardown()
        self.manager.garbage.append(self._output_dir)
