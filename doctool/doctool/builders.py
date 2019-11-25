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
:summary: Groups all Project's Builder Classes

"""
import sys
import threading
import logging

from doctool import settings
from doctool.helpers import Types
from doctool.interfaces import IBuilder

logger = logging.getLogger(__name__)


class BuilderThread(threading.Thread):
    """
    A Thread builder Class
    """

    def __init__(self, builder, project=None, group=None, target=None, name=None, args=None, kwargs=None):
        """
        Constructor

        :param builder: The builder instance
        :type builder: IBuilder

        :param project: The project instance
        :type project: doctool.models.RSTProject or doctool.models.CodeProject

        *group* should be None; reserved for future extension when a ThreadGroup
        class is implemented.

        *target* is the callable object to be invoked by the run()
        method. Defaults to None, meaning nothing is called.

        *name* is the thread name. By default, a unique name is constructed of
        the form "Thread-N" where N is a small decimal number.

        *args* is the argument tuple for the target invocation. Defaults to ().

        *kwargs* is a dictionary of keyword arguments for the target
        invocation. Defaults to {}.
        """
        super(BuilderThread, self).__init__(group=group, target=target, name=name, args=args, kwargs=kwargs)
        self._builder = builder
        self._project = project

        self.out = Types.AttributeString()
        self.out.uid = project.id
        self.out.rcode = -1
        self.out.failed = True
        self.out.succeeded = False

        logger.debug('Thread {0} initialized')

    @property
    def project(self):
        """
        Holds projects instances to build

        :return: RSTProject and/or CodeProject instance
        :rtype: doctool.models.RSTProject or doctool.models.CodeProject

        .. seealso:: :class:`doctool.models.RSTProject` Class
        .. seealso:: :class:`doctool.models.CodeProject` Class
        """
        return self._project

    def run(self):
        """
        Threading Override Method

        :return: The thread status
        :rtype: int
        """
        # Getting the project's data

        logger.debug('Thread {0} running ...')

        self.project.setup()
        self.project.build()
        self.project.teardown()

        data = self.project.data
        # Write the Specification file (conf.py)
        self._builder.write_spec(data.source_dir, data, override=True)
        # Run Doctool Sphinx Engine from command line
        self.out = self._builder.run_sphinx(**data)
        self.out.uid = self.project.id
        return self.out.rcode


class SphinxBuilder(IBuilder):
    """
    Sphinx Builder for Project generation
    """

    @classmethod
    def create_template_manager(cls, templates_directory=None, builder=None):
        """
        Creates a Template Manager instance with provided or default parameters

        :param builder: An instance of IBuilder sub-class
        :type builder: IBuilder or SphinxBuilder

        :param templates_directory: The Templates directory, which holds all the templates files
        :type templates_directory: str or unicode

        :return: A TemplateManager instance
        :rtype: doctool.managers.TemplateManager
        """
        from doctool.managers import TemplateManager
        return TemplateManager(templates_directory=templates_directory or settings.TEMPLATES_DIR,
                               builder=builder)

    def __init__(self, manager, build_info, helper):
        """
        Constructor

        :param manager: The manager instance
        :type manager: doctool.managers.ProjectManager

        :param build_info: The build info
        :type build_info: dict

        :param helper: ProjectHelper instance
        """
        self._manager = manager
        self._extensions_manager = manager.extensions_manager
        self._helper = helper

        self._build_info = {}
        # Using Property Setter to ensure
        # the passed parameter is of a good type
        self.build_info = build_info
        self._extensions_manager.init(build_info)

        # Holding a template manager
        self._template_mgr = None

    @property
    def helper(self):
        """
        Wraps Main Manager Helper instance into a clearer self property if needed

        :return: ProjectHelper instance
        """
        return self._helper

    @property
    def template_mgr(self):
        """
        Property holding the Template Manager instance

        .. note:: A Template Manager instance is instanciated if needed

        :return: A Template Manager instance
        :rtype: TemplateManager
        """
        if not self._template_mgr:
            self._template_mgr = self.create_template_manager(builder=self)
        return self._template_mgr

    @property
    def build_info(self):
        """
        Property holding the build information

        :return: The Build information as dictionary
        :rtype: dict
        """
        return self._build_info

    @build_info.setter
    def build_info(self, info):
        """
        Property Setter for the build information

        :param info: The Build information as dictionary
        :type info: dict
        """
        assert issubclass(info.__class__, dict), ("You must pass a dict or "
                                                  "subclass of it as build_info parameter!")
        self._build_info = info

    def run_sphinx(self, **cmd_options):
        """
        Simply calls local command-line execution of

        .. code-block:: bash
            :linenos:

            ${sphinx} -b html <source> <build_output>

        :param cmd_options: All extra Sphinx Commandline options
        :type cmd_options: Types.AttributeDict

        :return: A Types.AttributeDict object containing all data for running Sphinx Cmdline
        :rtype: Types.AttributeDict

        .. caution:: You should provide the ``GRAPHVIZ`` binary path, if you expect some UML diagrams!
        """
        cmd = (
            r'{python} "{sphinx_exe}" -b {output_format} -a {source_dir} {output_dir} '
            # r'-D {doctool2sphinx} '
            # r'-A {doctool2sphinx}'
        )

        sphinx_exe = self.helper.get_executable_path('sphinx-build')
        if not sphinx_exe or not self.helper.exists(sphinx_exe):
            raise ValueError('No Sphinx builder installed! (pip install sphinx)')

        data = dict(
            python=sys.executable,
            sphinx_exe=sphinx_exe,
            # doctool2sphinx='{0}={1}'.format(self._manager.master_title_slug, cmd_options.get('uid'))
        )
        data.update(cmd_options)

        return self.helper.run_command(cmd.format(**data), cwd=data['source_dir'])

    def write_spec(self, out_dirname, data, template_name='config/conf.tpl', override=False):
        """
        Generates conf.py file accordingly to passed parameters.

        :param out_dirname: Where the file is written (absolute/relative path)
        :type out_dirname: str

        :param data: Data for template engine
        :type data: Types.AttributeDict

        :param template_name: the template relative path
        :type template_name: str

        :param override: if set, the file is overridden no matter what.
        :type override: bool
        """
        # It ensures the final output directory is created
        self.helper.createdirs(out_dirname)

        conf_file = self.helper.absjoin(out_dirname, 'conf.py')
        template = self.template_mgr.template_by_name(template_name)

        data['doctool_rootdir'] = settings.DOCTOOL_ROOTDIR
        data['templates_dir'] = settings.TEMPLATES_DIR

        graphviz = self._extensions_manager.get_extension('graphviz')
        if graphviz:
            data['graphviz_dot'] = graphviz.dot

        plantuml = self._extensions_manager.get_extension('plantuml')
        if plantuml:
            data['java_bin'] = plantuml.java_bin
            data['plantuml_jar'] = plantuml.plantuml_jar

        data['projects'] = self._manager.ranked_projects

        self.helper.write_file(conf_file, template.render(data), override=override, mode='w+')

    def build_synchronous_unit(self, project=None):
        """
        Defines the Build process.

        :param project: A project instance (IProject sub-class)
        :type project: IProject sub-class

        :return: The build status
        :rtype: IBuilder.Status

            * IBuilder.Status.UNKNOWN: -2
            * IBuilder.Status.FAILURE: -1
            * IBuilder.Status.SUCCESS: 0
        """
        # Getting the project's data
        data = project.data
        # Write the Specification file (conf.py)
        self.write_spec(data.source_dir, data, override=True)
        # Run Doctool Sphinx Engine from command line
        return self.run_sphinx(**data)

    def build_asynchronous(self, projects=None):
        """
        Builds the list of projects asynchronously.

        :param projects: A collection of project instances (IProject sub-class)
        :type projects: tuple, list

        :return: The build status
        :rtype: IBuilder.Status

            * IBuilder.Status.UNKNOWN: -2
            * IBuilder.Status.FAILURE: -1
            * IBuilder.Status.SUCCESS: 0
        """

        projects = projects or []
        has_failed = False
        threads_list = []

        if projects:
            for proj in projects:
                thread = BuilderThread(self, project=proj)
                threads_list.append(thread)
                thread.start()

            for thread in threads_list:
                thread.join()

            has_failed = len([thread for thread in threads_list if thread.out.failed]) > 0

            for idx, thread in enumerate(threads_list):
                uid, out = thread.out.uid, thread.out
                report = '{0}. Project UID : {1} '.format(idx + 1, uid)
                if out.failed:
                    printer = logger.error
                    report += 'has failed for those reasons : {0}'.format(out)
                else:
                    printer = logger.info
                    report += 'has been successfully built!'

                printer(report)

        return self.Status.FAILURE if has_failed else self.Status.SUCCESS

    def build(self, projects=None):
        """
        Builds the list of projects.

        :param projects: A collection of project instances (IProject sub-class)
        :type projects: tuple, list

        :return: The build status
        :rtype: IBuilder.Status

            * IBuilder.Status.UNKNOWN: -2
            * IBuilder.Status.FAILURE: -1
            * IBuilder.Status.SUCCESS: 0
        """
        projects = projects or []
        status_list = []
        has_failed = False

        if projects:
            for proj in projects:
                proj.setup()
                proj.build()
                proj.teardown()

                logger.debug('Building Project : "{0}"\n'.format(proj.id))
                logger.debug('FIRST LINK : {0}'.format(proj.first_link))

            for proj in projects:
                out = self.build_synchronous_unit(proj)
                status_list.append(Types.AttributeDict(uid=proj.id, out=out))

            has_failed = len([st for st in status_list if st.out.failed]) > 0

            for idx, status in enumerate(status_list):
                uid, out = status.uid, status.out
                report = '{0}. Project UID : {1} '.format(idx + 1, uid)
                if out.failed:
                    printer = logger.error
                    report += 'has failed for those reasons : {0}'.format(out)
                else:
                    printer = logger.info
                    report += 'has been successfully built!'

                printer(report)

                logger.debug('Sphinx output:')
                logger.debug(out)

                logger.debug('Sphinx error output:')
                logger.debug(out.stderr)

        return self.Status.FAILURE if has_failed else self.Status.SUCCESS
