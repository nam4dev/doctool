#!/usr/bin/env python
# -*- coding: utf-8 -*-
import doctool.helpers
import doctool.settings

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
:summary: Groups all Project's Management Classes
"""
import os
import json
import jinja2
import logging

from doctool import settings

from doctool.interfaces import IManager
from doctool.interfaces import IProject
from doctool.interfaces import IBuilder

from doctool.builders import SphinxBuilder

from doctool.helpers import Types
from doctool.helpers import ProjectHelper
from doctool.helpers import CodeProjectHelper

from doctool.models import Theme
from doctool.models import RSTProject
from doctool.models import CodeProject

from doctool.errors import UnknownThemeError
from doctool.errors import UnknownParameterError
from doctool.errors import MissingParameterError
from doctool.errors import MissingConfigurationError

logger = logging.getLogger(__name__)


class ProjectManager(IManager):
    """
    This Class handles how Projects are handled and managed to produce
    desired HTML corresponding views
    """
    doctool_build_info = ProjectHelper.absjoin(settings.DOCTOOL_ROOTDIR, 'build')

    __initial_report = '''

    ** Doctool uses as initial inputs **

    #. Project Mode : {mode}
    #. Generated Project(s) : {ranked_projects}
    #. Master Documentation Title : {this.master_title}
    #. Theme used : {this.theme.name}
    #. Output destination directory : {this.output_dir}
    #. Interactive Mode : {interactive}

    '''

    __final_report = '''

    ** Doctool Generated Output **

    Your Documentation has been successfully built at : {0}
    You can visualize it by opening this link in your favorite Web browser:
    <link>{1}</link>

    '''

    class Mode(object):
        """
        Project mode indicates if we're dealing with a Single project or multiple
        """
        SIMPLE = 0xAA
        MULTIPLE = 0xAB

    def __init__(self,
                 output_format="html",
                 list_projects=None,
                 project="",  # FIXME: not used for now
                 version=settings.DEFAULT_VERSION,
                 projects=None,
                 output="",
                 conf_file="",
                 master_title="",
                 theme_name="bootstrap",
                 interactive=1):
        """
        Doctool Projects Manager Constructor.

        :param output_format: In which format the documentation is to be generated.
        :type output_format: str

        :param list_projects: Gets an exhaustive list of known projects from your Configuration file.
        :type list_projects: bool

        :param project: Provides either a key from your Configuration file
            or a directory path containing ReSt files.
        :type project: str

        :param version: The version of the documentation to build
        :type version: str

        :param projects: Provides either a combination of keys from your Configuration file
            or a combination of directories path containing ReSt files.
        :type projects: list

        :param output: Provides output directory path where your documentation is to be generated.
        :type output: str

        :param conf_file: Provides the configuration file path.
        :type conf_file: str

        :param master_title: Provides the title to your whole generated documentation.
        :type master_title: str

        :param theme_name: Provides the theme name to your whole generated documentation.
        :type theme_name: str

        :param interactive: Gets the interactive mode.
        :type interactive: int
        """
        self._helper = None
        self._api_helper = None
        self._theme_manager = None
        self._extensions_manager = None
        self._theme = None
        self._builder = None
        self._global_conf = None
        self._projects_from_build_info = None
        self._projects_collection = []
        self._ranked_projects = []
        self._garbage = []

        self._list_projects = list_projects
        self._conf_file = conf_file or settings.DEFAULT_CONFIG

        assert os.path.exists(self._conf_file), "The Configuration file does not exists ({0})".format(self._conf_file)

        # Loading Global Configuration
        self._load()

        # Support User (~) & env variable expansion
        # The resulting path is then normed.
        self._working_dir = ProjectHelper.normpath(
            os.path.expandvars(
                os.path.expanduser(
                    self.global_conf.get('WORKING_DIR', os.path.dirname(self._conf_file))
                )
            )
        )

        self.version = version
        self._projects_ids = projects
        self._output = output or self.global_conf.OUTPUT

        if not os.path.isabs(self._output):
            self._output = settings.absjoin(self._working_dir, self._output)

        if version == settings.DEFAULT_VERSION:
            logger.warning(
                'Using default version %s. To change this behavior, '
                'pass --version CLI switch to doctool' % version
            )

        if not self._output.endswith(version):
            self._output = settings.absjoin(self._output, version)

        # handling wildcard `*` for all projects
        if len(self._projects_ids) == 1 and self._projects_ids[0].strip() == '*':
            self._projects_ids = self.global_conf.PROJECTS_MAP.keys()

        self._master_title = master_title or self.global_conf.MASTER_TITLE
        self._output_format = output_format
        self._theme_name = theme_name
        self._interactive = interactive

        if not list_projects:
            projects_count = len(self._projects_ids)
            assert projects_count > 0, "You MUST specify at least one project!"
            self._mode = ProjectManager.Mode.MULTIPLE if projects_count > 1 else ProjectManager.Mode.SIMPLE

    @property
    def helper(self):
        """
        Helper property

        :return: The Project Helper instance
        """
        return self._api_helper or self._helper

    @property
    def garbage(self):
        """
        Helper property

        :return: The Project Helper instance
        """
        return self._garbage

    @property
    def projects_collection(self):
        """
        Property holding the project's collection

        :rtype: list
        :return: The collection of project instance(s)
        """
        return self._projects_collection

    @property
    def ranked_projects(self):
        """
        Sorts all projects based on its rank attribute

        :rtype: list
        :return: The ranked projects list
        """
        if not self._ranked_projects:
            self._ranked_projects = sorted(
                self.projects_collection,
                key=lambda item: item.rank
            )
        return self._ranked_projects

    @property
    def extensions_manager(self):
        """
        Extensions Manager property

        :return: The Extensions Manager instance
        """
        return self._extensions_manager

    @property
    def output_dir(self):
        """
        The global output path (absolute path)

        :rtype: str or unicode
        :return: A valid output path
        """
        return self._output

    @property
    def projects_from_build_info(self):
        """
        Helper property

        :return: The Project Helper instance
        """
        if not self._projects_from_build_info:
            self._projects_from_build_info = self.global_conf.PROJECTS_MAP
        return self._projects_from_build_info

    @property
    def theme(self):
        """
        The global Project's Theme instance

        :rtype: Theme
        :return: The global Project's Theme instance
        """
        return self._theme

    @property
    def master_title(self):
        """
        The global Project's Name & Title

        :rtype: str
        :return: The global Project's Name & Title
        """
        return self._master_title

    @property
    def master_title_slug(self):
        """
        The global Project's Name & Title

        :rtype: str
        :return: The global Project's Name & Title
        """
        return self.helper.slugify(self._master_title)

    @property
    def output_format(self):
        """
        The global output format {HTML, PDF, ...}

        :rtype: str
        :return: The global output format
        """
        return self._output_format

    @property
    def mode(self):
        """
        Gets the instance mode (Mode.SIMPLE | Mode.MULTIPLE)

        :rtype: int
        :return: In which mode the instance is running for
        """
        return self._mode

    @property
    def global_conf(self):
        """
        Property holding the global configuration/settings

        :rtype: Types.AttributeDict
        :return: The settings instance
        """
        return self._global_conf

    @property
    def is_simple(self):
        """
        Is the instance in Single Mode ?

        :rtype: bool
        :return: True if the Current instance mode is Mode.SIMPLE
        """
        return self._mode == self.Mode.SIMPLE

    @property
    def is_multiple(self):
        """
        Is the instance in Multi Mode ?

        :rtype: bool
        :return: True if the Current instance mode is Mode.MULTIPLE
        """
        return self._mode == self.Mode.MULTIPLE

    def data_context_builder(self, **options):
        """
        Build the data context to be injected into templating system

        :param options: Any additional options to be injected

        :rtype: Types.AttributeDict
        :return: A data context instance
        """
        context = self.global_conf.copy()
        context.update({
            'VERSION': self.version,
            'master_title': self.master_title_slug
        })
        context.update(options)
        return Types.AttributeDict(**context)

    def _create_project(self, project_conf, project_cls=RSTProject):
        """
        Creates a Project instance, stores it into its inner collection and returns it

        :rtype: RSTProject or CodeProject
        :return: The project instance
        """
        assert issubclass(project_cls, IProject), "You must provide a sub-class of IProject!"

        project = project_cls(self, project_conf)
        self._projects_collection.append(project)

        return project

    def _load(self):
        """
        Loads the Global Projects Configuration file (JSON)

        :raise MissingParameterError: if no valid settings are found
        """
        if not self._global_conf:
            with open(self._conf_file, 'r') as handle:
                self._global_conf = Types.AttributeDict(json.loads(handle.read()))
        else:
            raise MissingParameterError("The Configuration file is Missing!"
                                        "\nFor further information go to:"
                                        "\nhttps://github.com/nam4dev/autodoc-aggregator")

    def copy_js_scripts(self):
        """
        Method in charge of copying JS
        (common, doctool, doctool-search) scripts to project directory
        """
        for script in ('doctool.js', 'doctool-common.js', 'doctool-search.js',):
            destination = self.helper.absjoin(self.output_dir, script)
            source = self.helper.absjoin(settings.TEMPLATES_DIR, 'config', script)
            self.helper.copy(source, destination)
            logger.debug('Copy JS script %s to %s...', source, destination)

    def write_js_settings_scripts(self):
        """
        Method in charge of writing JS Settings scripts to project directory
        """
        logger.debug('Writing JS Settings scripts...')

        template_mgr = self._builder.template_mgr
        settings_filename = self.helper.absjoin(self.output_dir, 'doctool-settings.js')
        settings_template = template_mgr.template_by_name('config/doctool-settings.js')
        template_html = settings_template.render(self.data_context_builder())
        self.helper.write_file(settings_filename, template_html, mode='w', override=True)

    def write_js_versions_scripts(self):
        """
        Method in charge of writing JS Settings scripts to project directory
        """
        logger.debug('Writing JS Versions scripts...')

        doctool_versions = 'doctool-versions.js'
        template_mgr = self._builder.template_mgr
        versions_filename = self.helper.absjoin(self.output_dir, '..', doctool_versions)
        versions_template = template_mgr.template_by_name('config/%s' % doctool_versions)
        template_html = versions_template.render(
            available_versions=sorted([
                version for version in os.listdir(self.helper.absjoin(self.output_dir, '..'))
                if version not in (doctool_versions,)
            ], reverse=True)
        )
        self.helper.write_file(versions_filename, template_html, mode='w', override=True)

    def write_js_scripts(self):
        """
        Template method in charge of grouping all JS writing operations
        """
        self.write_js_versions_scripts()
        self.write_js_settings_scripts()

    def _write_global_index(self):
        """
        Builds on top of all Generated Projects an Ajax layer to put them all together
        and build a Dynamic and User-friendly Navigation Bar.
        """
        logger.debug('Wrapping multiple projects into an aggregated Web Application...')

        self.copy_js_scripts()
        self.write_js_scripts()
        self._write_global_search()

        template_mgr = self._builder.template_mgr
        index_filename = self.helper.absjoin(self.output_dir, 'index.html')
        index_template = template_mgr.template_by_name('config/index_wrapper.html')
        template_html = index_template.render(
            self.data_context_builder(redirect=self.ranked_projects[0].first_link)
        )
        self.helper.write_file(index_filename, template_html, mode='w', override=True)

    def _write_global_search(self):
        """
        Builds a Global search files based on all projects
        """
        logger.debug('Wrapping global search files...')
        doc_projects, api_doc_projects, home_project = [], [], None
        for p in self.ranked_projects:
            if p.home:
                home_project = p
            elif p.is_api:
                api_doc_projects.append(p)
            else:
                doc_projects.append(p)

        # Generate the search file only if at least 2 searchable projects are present
        if len([p.search for p in doc_projects + api_doc_projects]) < 2:
            return

        static = self.helper.absjoin(self.output_dir, self.ranked_projects[0].id, '_static')
        if os.path.isdir(static):
            target = self.helper.absjoin(self.output_dir, '_static')
            self.helper.cptree(static, target)
            self.helper.cptree(static, target)

        template_mgr = self._builder.template_mgr
        index_filename = self.helper.absjoin(self.output_dir, 'search.html')
        index_template = template_mgr.template_by_name('config/full_search_wrapper.html')

        current_project_name = ''
        if len(self.ranked_projects) == 1:
            current_project_name = self.ranked_projects[0].name

        template_html = index_template.render(
            self.data_context_builder(
                home_project=home_project,
                doc_projects=doc_projects,
                api_doc_projects=api_doc_projects,
                current_project_name=current_project_name
            )
        )
        self.helper.write_file(index_filename, template_html, mode='w', override=True)

    def _initial_report(self):
        """
        Prints Initial Doctool state.
        In other words, what values were passed at the init time
        """
        ranked_projects = ""
        for idx, proj in enumerate(self.ranked_projects):
            if idx == 0:
                ranked_projects += '\n\n'
            ranked_projects += '\t\t{0}. {1}\n'.format(idx + 1, proj.name)

        logger.info(self.__initial_report.format(this=self,
                                                 mode='SIMPLE' if self.is_simple else 'MULTIPLE',
                                                 ranked_projects=ranked_projects,
                                                 interactive='Yes' if self._interactive else 'No'))

    def _print_report(self):
        """
        Prints a User-Friendly Execution Report at the end of the process
        """
        data = (self.output_dir,
                self._helper.absjoin(self.output_dir, 'index.html'))
        logger.info(self.__final_report.format(*data))

    def setup(self):
        """
        Setups the Projects Manager.

        Ensures all needed directories
        """
        self._helper = ProjectHelper()
        self._api_helper = CodeProjectHelper()

        if not self._output:
            self._output = settings.DEFAULT_OUTPUT_DIRNAME

        self._theme_manager = ThemeManager()
        self._extensions_manager = ExtensionManager()
        self._builder = SphinxBuilder(self, self.global_conf, self.helper)

        self._theme = self._theme_manager.get_theme(self._theme_name or self.global_conf.THEME)

        output_dir = self.output_dir
        if os.path.isdir(output_dir):
            remove = True
            if self._interactive:
                user_response = input('The Destination folder : {0} already exists ! \n'
                                      'Do you wanna remove it ? (Y/n)'.format(output_dir))
                if user_response not in ('Yes', 'yes', 'y'):
                    remove = False
            if remove:
                if self.helper.rmtree(output_dir):
                    logger.info('Folder ({0}) successfully removed!'.format(output_dir))
                else:
                    logger.exception('Error while removing directory : {0} !'.format(output_dir))

        self.helper.createdirs(output_dir)

    def build(self):
        """
        Override.

        Builds the projects Session.

        :raise UnknownParameterError: If an Unknown project key or an Invalid directory path is provided
        """
        for project_id in self._projects_ids:
            project_conf_hint = {'working_dir': self._working_dir}
            if os.path.isdir(project_id):
                # Handle here a directory path
                project_conf_hint['dir2parse'] = project_id
            elif project_id in self.projects_from_build_info:
                # Handle here a configuration item
                project_conf_hint['dir2parse'] = self.projects_from_build_info.get(project_id)
            else:
                raise UnknownParameterError('The Specified project {0} is '
                                            'unknown from your Global configuration file and/or '
                                            'does not have its own configuration file!'.format(project_id))

            project_conf = ProjectHelper.load_from_file(project_conf_hint)
            _ = self._create_project(project_conf, CodeProject if project_conf.get('api') else RSTProject)

        self._initial_report()
        logger.info('Generating Documentation (this operation may take a while) ...')
        return self._builder.build(self.ranked_projects)
        # self._builder.build_asynchronous(self.ranked_projects)

    def teardown(self):
        """
        * Implements a way to aggregate all generated Projects if the Mode is MULTIPLE
        * Cleans all remaining temporary file(s)
        """
        if self.is_simple or self.is_multiple:
            self._write_global_index()

        for item in self._garbage:
            self.helper.remove(item)

        self._print_report()

    def run(self):
        """
        Entry point
        Run either the project listing from settings or the building process
        """
        if self._list_projects:
            projects = self.global_conf.PROJECTS_MAP.values()
            projects_count = len(projects)
            projects_list = ('{1} project(s) found in your Configuration file ({0})'
                             ':\n\n').format(self._conf_file, projects_count)

            ranked = []
            for dir2parse in projects:
                project = ProjectHelper.load_from_file({'dir2parse': dir2parse})
                ranked.append(project)

            for index, project in enumerate(sorted(ranked, key=lambda p: p.rank)):
                projects_list += '{3}. {0}: {1} (Ranking index : {2})\n'.format(project.id, project.name, project.rank,
                                                                                index + 1)
            logger.info(projects_list)
        else:
            self.setup()
            if self.build() == IBuilder.Status.SUCCESS:
                self.teardown()


class TemplateManager(object):
    """
    Manages Templates engine
    """
    engine = None
    loader = None
    builder = None

    def __init__(self, templates_directory=None, builder=None):
        """
        Constructor

        :param builder: The Parent Builder instance
        :type builder: SphinxBuilder
        """
        TemplateManager.set_builder(builder)
        TemplateManager.init(templates_directory)

    @classmethod
    def set_builder(cls, builder):
        """
        Class Attribute Setter

        :param builder: The Parent Builder instance
        :type builder: SphinxBuilder
        """
        if not TemplateManager.builder:
            assert (builder and
                    issubclass(builder.__class__, IBuilder)
                    ), "Your Builder instance must be an IBuilder sub-class instance!"
            cls.builder = builder

    @classmethod
    def init(cls, templates_directory):
        """
        Initializes The Template Manager Engine

        :param templates_directory: The templates directory path

        .. note:: :mod:`jinja2` module is used.
        """
        if not TemplateManager.engine:
            assert (templates_directory and
                    os.path.isdir(templates_directory)), "Your Templates directory is invalid!"
            cls.loader = jinja2.FileSystemLoader(templates_directory)
            cls.engine = jinja2.Environment(loader=cls.loader, extensions=[])

    @classmethod
    def template_by_name(cls, template_name):
        """
        Gets a template by its name (the relative path from which the templates are stored)

        :param template_name: The template name (relative path to _templates folder

        :return: The Template instance
        """
        assert cls.engine is not None, ("You MUST initialize (by calling init(templates_directory)) "
                                        "The TemplateManager Class, prior to call template_by_name method!")
        return cls.engine.get_template(name=template_name)


class ThemeManager(object):
    """
    The Themes Manager
    """

    __BUILTIN_THEMES = (
        'default',
        'sphinxdoc',
        'nature',
        'basic',
        'scrolls',
        'agogo',
        'pyramid',
        'haiku',
        'traditional',
        'epub'
    )

    specs = Types.AttributeDict(
        nature=Theme(ref='nature',
                     name='nature',
                     html_theme_opts=dict()
                     ),
        guzzle=Theme(ref='guzzle_sphinx_theme',
                     name='guzzle',
                     html_theme_method='html_theme_path',
                     html_translator_class='guzzle_sphinx_theme.HTMLTranslator',
                     html_theme_opts=dict(project_nav_name="{0}",
                                          navbar_class='',
                                          touch_icon='',
                                          base_url=''),
                     pygments_style='guzzle_sphinx_theme.GuzzleStyle',
                     extends=True
                     ),
        bootstrap=Theme(ref='sphinx_bootstrap_theme',
                        name='bootstrap',
                        html_theme_method='get_html_theme_path',
                        html_translator_class='',
                        html_theme_opts=dict(navbar_title='{0}',
                                             navbar_site_name='Packages',
                                             globaltoc_depth=2,
                                             navbar_pagenav='false',
                                             navbar_sidebarrel='false',
                                             globaltoc_includehidden='false',
                                             navbar_class='navbar',
                                             navbar_fixed_top='true',
                                             source_link_position='footer'),
                        pygments_style='friendly'
                        ),
        mozilla=Theme(ref='mozilla_sphinx_theme',
                      name='mozilla',
                      html_theme_method='__file__',
                      simple=True)
    )

    @classmethod
    def get_theme(cls, theme_name):
        """
        Gets the theme according the name passed if present else raise UnknownThemeError.

        :param theme_name: The Theme name
        :type theme_name: str

        :raise UnknownThemeError: If provided theme name is unknown

        :return: The Theme instance
        :rtype: Theme

        .. topic:: Available Themes :

            * nature
            * guzzle
            * bootstrap
            * mozilla
        """
        stripped_theme_name = theme_name.strip()
        assert stripped_theme_name in cls.specs, UnknownThemeError('The provided theme name : '
                                                                   '{0} is Unknown!'.format(theme_name))
        theme = cls.specs[stripped_theme_name]
        theme.custom = theme.name not in cls.__BUILTIN_THEMES
        return theme


class ExtensionManager(object):
    """
    The Sphinx Extensions Manager

    Managed extension :

        * Graphviz
        * Plantuml
    """

    _extensions = {}
    _configuration = None

    @classmethod
    def __manage_graphviz(cls):
        """
        This method manage Graphviz configuration:

            * Searching in Configuration file for data
            * Is the provided value an absolute path or an Environment Variable key?
            * Validating path
            * Ensuring default values to be set
        """
        # Getting Config data if any
        conf = Types.AttributeDict(cls._configuration.get('GRAPHVIZ', {}))
        # We've got configuration data
        dot_path = conf.get('dot')
        if not ProjectHelper.exists(dot_path):
            # Getting Default Dot from Environment Variables if any.
            exe_path = ProjectHelper.get_executable_path('dot')
            if exe_path.succeeded and ProjectHelper.exists(exe_path):
                conf.dot = dot_path = exe_path

        # Check if Graphviz Extension is properly functional (for dependencies)
        if ProjectHelper.exists(dot_path):
            cls._extensions['GRAPHVIZ'] = conf
            logger.info('GRAPHVIZ : `DOT` executable found at {0} !'.format(dot_path))
        else:
            logger.info('GRAPHVIZ : `DOT` executable NOT found !')
            logger.info('Graphs and/or UML Diagrams are therefore NOT enabled!')

    @classmethod
    def __manage_plantuml(cls):
        """
        This method manage PlantUML configuration:

            * Searching in Configuration file for data
            * Is the provided value an absolute path or an Environment Variable key?
            * Validating path
            * Ensuring default values to be set
        """
        # first reading Configuration, setting default behavior if not found in config
        plantuml_conf = Types.AttributeDict(cls._configuration.get('PLANTUML', {}))
        # Graphviz is mandatory, in order to use Plant UML

        if 'GRAPHVIZ' in cls._extensions and plantuml_conf:
            # In most of case, on WINDOWS platforms Java is installed at:
            # C:\windows\system32\java.exe
            java_bin = plantuml_conf.get('java', settings.LOGICAL_JAVA_BIN_PATH)

            if not ProjectHelper.exists(java_bin):
                out = ProjectHelper.get_executable_path('java')
                if out.succeeded and ProjectHelper.exists(out):
                    plantuml_conf['java_bin'] = out

                    # We can check JAR only now, cause without Java there's no need to have a valid JAR
                    # first from Configuration
                    hints = (plantuml_conf.get('jar'),
                             # then, from Environment Variable
                             os.environ.get('DOCTOOL_PLANTUML_JAR'),
                             # Lastly attempting default behavior
                             os.path.abspath(os.path.expanduser('~/.doc/pypi/doctool/plantuml.jar')))

                    for hint in hints:
                        if ProjectHelper.exists(hint):
                            plantuml_conf['plantuml_jar'] = hint
                            break

        uml_disabled = 'UML Diagrams are therefore NOT enabled!'
        if ProjectHelper.exists(plantuml_conf.get('java_bin')):
            logger.info('JAVA: found at {java_bin}!'.format(**plantuml_conf))
            if ProjectHelper.exists(plantuml_conf['plantuml_jar']):
                logger.info('PLANTUML: found at {plantuml_jar}!'.format(**plantuml_conf))
                cls._extensions['PLANTUML'] = plantuml_conf
            else:
                logger.warning('PLANTUML NOT FOUND!')
                logger.warning(uml_disabled)
        else:
            logger.warning('JAVA NOT FOUND!')
            logger.warning(uml_disabled)

    @classmethod
    def init(cls, configuration):
        """
        Initializes the ExtensionManager Component with the given Configuration data

        :param configuration: The Extension(s) data from Configuration file
        :param configuration: dict, Types.AttributeDict
        """
        cls._configuration = configuration

        if not cls._configuration:
            raise MissingConfigurationError()

        cls.__manage_graphviz()
        cls.__manage_plantuml()

    @classmethod
    def extensions(cls):
        """
        Gets all extensions data stored in the Manager

        .. note:: Acts as a Class Method Getter/Property

        :return: A set of Extensions data
        :rtype: dict, Types.AttributeDict
        """
        return cls._extensions

    @classmethod
    def get_extension(cls, extension_name):
        """
        Gets an extension data set

        :param extension_name: The Extension name (graphviz, plantuml, ...)
        :type extension_name: str

        :return: The Extension data
        :rtype: dict, Types.AttributeDict or None
        """
        return cls._extensions.get(extension_name.upper())
