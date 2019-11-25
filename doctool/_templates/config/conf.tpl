#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

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
:summary: Sphinx conf.py

Configure the way documentation will be generated
"""
import os
import re
import sys

counter = 0
DOCTOOL_ROOTDIR = r'{{ doctool_rootdir }}'.replace('\\', '/')

re_relative_path = re.compile(r'(\.\./|\./)')
re_file_directives = re.compile(r'(.. include::|.. literalinclude::|.. image::|.. figure::|:download:)')


def append_sys_paths(source_dir=None):
    """
    Append all needed sys.path

    :param source_dir:
    :return:
    """
    if not source_dir or not os.path.isdir(source_dir) or source_dir in sys.path:
        return
    global counter
    sys.path.insert(counter, source_dir)
    print("PYTHON PATH {0} inserted at position {1}".format(source_dir, counter))
    counter += 1


# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
append_sys_paths(DOCTOOL_ROOTDIR)

# Here, goes all Core Framework imports
from doctool import settings
from doctool.roles import jira
from doctool.directives import epydoc
from doctool.directives import releases
from doctool.helpers import ProjectHelper as Helper

{% if not javasphinx %}
{% if dirs2append %}
{% for directory in dirs2append %}
append_sys_paths(source_dir=r'{{directory}}')
{% endfor %}
{% endif %}
{% if extra_paths %}
{% for p in extra_paths %}
append_sys_paths(source_dir=Helper.handle_path(r'{{p}}'))
{% endfor %}
{% endif %}
{% endif %}


def doctool_doctree(app, doctree, docname=None):
    """
    Doctool doctree hook

    :param app:
    :param doctree:
    """

    paths = [settings.REPO_BASE]
    {% if projects %}
    {% for proj in projects %}
    paths.append(r'{{proj.src_dirname}}')
    {% endfor %}
    {% endif %}

    try:
        # FIXME
        import xml.etree.ElementTree as ET
        xml_node = ET.fromstring('{0}'.format(doctree))
        targets = xml_node.xpath('//download_reference//attribute::reftarget')
        for possible_link_node in targets:
            if not os.path.exists(possible_link_node):
                cleaned_link = re_relative_path.sub('', possible_link_node)

                for base in paths:
                    guess = Helper.absjoin(base, cleaned_link)
                    if os.path.exists(guess):
                        possible_link_node.getparent().attrib['reftarget'] = guess
                        break

    except Exception as exc:
        print('XML Handled Exception : {0}'.format(exc))


def setup(app):
    # Allow to connect an handler on pre-process `autodoc-process-docstring` signal
    # app.connect('autodoc-process-docstring', debug_docstring)
    """

    :param app:
    """
    paths = []
    {%if projects %}
    {% for proj in projects %}
    paths.append(r'{{proj.src_dirname}}')
    {% endfor %}
    {% endif %}

    epydoc.setup(app, projects_paths=paths)
    releases.setup(app, projects_paths=paths)

    app.add_role('jira_issue', jira.issue_role)
    app.add_role('jira_story', jira.story_role)

    app.add_config_value('jira_project_url', None, 'env')

    app.connect('doctree-resolved', doctool_doctree)


html_show_sourcelink = 0
jira_project_url = '{{ JIRA_PROJECT_URI }}'

# Useful to refer to docutils Online documentation
extlinks = {'duref': ('http://docutils.sourceforge.net/docs/ref/rst/'
                      'restructuredtext.html#%s', ''),
            'durole': ('http://docutils.sourceforge.net/docs/ref/rst/'
                       'roles.html#%s', ''),
            'dudir': ('http://docutils.sourceforge.net/docs/ref/rst/'
                      'directives.html#%s', '')}

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx.ext.extlinks',
    'sphinx.ext.todo',
    'sphinx.ext.imgmath',
    # 'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    # 'sphinx.ext.doctest',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
]
# Register the theme as an extension to generate a sitemap.xml
{% if extends %}
extensions.append("{{html_theme}}")
{% endif %}
{% if javasphinx %}
extensions.append('javasphinx')
{% endif %}
# Add any paths that contain templates here, relative to this directory.
templates_path = [r'{{templates_dir}}']
{% if graphviz_dot %}
graphviz_dot = r"{{graphviz_dot}}"
extensions.append('sphinx.ext.graphviz')
{% if graphviz_dot_args %}
graphviz_dot_args = {{graphviz_dot_args}}
{% endif %}
{% if graphviz_output_format %}
graphviz_output_format = "{{graphviz_output_format}}"
{% else %}
graphviz_output_format = "png"
{% endif %}
# PLANTUML Configuration
{% if java_bin and plantuml_jar %}
java_bin = r"{{java_bin}}"
plantuml_jar = r"{{plantuml_jar}}"
plantuml = "\"{2}\" -jar \"{1}\" -graphvizdot \"{0}\"".format(graphviz_dot, plantuml_jar, java_bin)
{% if plantuml_output_format %}
plantuml_output_format = "{{plantuml_output_format}}"
{% else %}
plantuml_output_format = "png"
{% endif %}
{% if plantuml_latex_output_format %}
plantuml_latex_output_format = "{{plantuml_latex_output_format}}"
{% else %}
plantuml_latex_output_format = "png"
{% endif %}
{% endif %}
{% endif %}

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = '{{master_doc}}'


# General information about the project.
project = '{{project_name}}'

{% if metadata %}
{% if metadata.copyright %}
copyright = '{{metadata.copyright}}'
{% else %}
copyright = '&copy; {{ ORGANISATION }} - {{ date }}'
{% endif %}
{% for a in metadata.authors %}
copyright += ', {{a}}'
{% endfor %}
# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.#
{% if metadata.version %}
# The short X.Y version.
version = '{{metadata.version}}'
{% endif %}
{% if metadata.release %}
# The full version, including alpha/beta/rc tags.
release = '{{metadata.release}}'
{% endif %}

{% if USE_GOOGLE_DOCSTRING %}
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_notes = True

extensions.append('sphinx.ext.napoleon')
{% endif %}

# -- Options for LaTeX output --------------------------------------------------
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [('index',
                    '{{project_name}}.tex',
                    '{{project_name}}',
                    '{% for a in metadata.authors %}{{a}} {% endfor %}',
                    'manual'), ]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [('index', '{{short_project_name}}',
              '{{project_name}}',
              ['{% for a in metadata.authors %}{{a}} {% endfor %}'],
              1)]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [('index', '{{project_name}}', '{{project_name}}',
                      '{% for a in metadata.authors %}{{a}} {% endfor %}', '{{project_name}}',
                      'Home Automation Control System.',
                      'Miscellaneous'), ]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'
{% else %}
copyright = '&copy; {{ ORGANISATION }} - {{ date }}'
version = '0.0'
release = '0.0.0'
{% endif %}

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
{% if theme.pygments_style %}
pygments_style = '{{theme.pygments_style}}'
{% endif %}

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = '{{theme.name}}'
html_context = {
    'HOST': '{{ HOST }}',
    'DEBUG': {{ DEBUG }},
    'VERSION': '{{ VERSION }}',
    'HOME_ICON': '{{ HOME_ICON }}',
    'ORGANISATION': '{{ ORGANISATION }}',
    'ISSUE_TRACKER_URI': '{{ ISSUE_TRACKER_URI }}',
    'ISSUE_TRACKER_TEXT': '{{ ISSUE_TRACKER_TEXT }}',
    'master_title': '{{ master_title }}',
    'TITLE': '{{ TITLE }}',
    'MASTER_TITLE': '{{ MASTER_TITLE }}',
    'current_project': None,
    'home_project': None,
    'doc_projects': [],
    'api_doc_projects': [],
    'current_project_name': '{{ project_name }}'
}
{% if projects %}
html_context['doc_projects'] = []
html_context['api_doc_projects'] = []
{% for proj in projects %}
c_project = dict(name='{{ proj.name }}',
                 id='{{ proj.id }}',
                 nav='{{ proj.nav }}',
                 icon='{{ proj.icon }}',
                 slug='{{ proj.slug }}',
                 search={{ proj.search }},
                 version='{{ metadata.version }}',
                 layout='{{ proj.layout }}',
                 menu=dict(left={{ proj.menu.left }}, right={{ proj.menu.right }}),
                 first_link=r'{{ proj.first_link }}',
                 is_api='{{ proj.is_api }}' == "1",
                 toctree=eval(compile("""{{ proj.toctree }}\n""", '<string>', 'eval')))
{% if proj.name == project_name %}
html_context['current_project'] = c_project
{% endif %}
{% if proj.home %}
html_context['home_project'] = c_project
{% elif proj.is_api %}
html_context['api_doc_projects'].append(c_project)
{% else %}
html_context['doc_projects'].append(c_project)
{% endif %}
{% endfor %}
{% endif %}

html_context['searchable_projects'] = [
    p for p in html_context['doc_projects'] + html_context['api_doc_projects'] if p.get('search')
]

# Available Themes are:
# import sphinx_bootstrap_theme
# import sphinx_rtd_theme
# import guzzle_sphinx_theme
# Add any paths that contain custom themes here, relative to this directory.

{% if theme.custom %}
html_theme_import = __import__('{{theme.ref}}')
{% if theme.simple %}
html_theme_path = [os.path.dirname(getattr(html_theme_import, '{{theme.html_theme_method}}'))]
{% else %}
{% if theme.name == "sphinx_rtd_theme" %}
html_theme_path = [getattr(html_theme_import, '{{theme.html_theme_method}}')()]
{% else %}
html_theme_path = getattr(html_theme_import, '{{theme.html_theme_method}}')()
{% endif %}
{% endif %}
{% endif %}

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

{% if theme.html_translator_class %}
# Adds an HTML table visitor to apply Bootstrap table classes
html_translator_class = '{{theme.html_translator_class}}'
{% endif %}

# Guzzle theme options (see theme.conf for more information)
{% if theme.html_theme_opts %}
html_theme_options = eval("{{theme.html_theme_opts}}")
{% endif %}
# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "{{project_name}}"

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = "{{project_name}}"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
{% if theme.html_logo %}
html_logo = r'{{theme.html_logo}}'
{% endif %}

# The name of an image file (within the _static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.

{% if theme.html_favicon %}
html_favicon = r'{{theme.html_favicon}}'
{% endif %}


# Add any paths that contain custom _static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin _static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = [r'{{html_static_path}}']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
html_split_index = True

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = 'pydoc'
html_use_modindex = True

# Add ``todos`` directives to generated output
todo_include_todos = True

# Example configuration for intersphinx: refer to the Python standard library.
{% if javasphinx %}
javadoc_url_map = {
    'com': ('http://docs.oracle.com/javase/7/docs/api/', 'javadoc'),
    'sphinx': ('', 'http://sphinx-doc.org/objects.inv'),
}
{% endif %}

intersphinx_mapping = {
    'python': ('https://docs.python.org/{{ PY_VERSION }}', None),
    'sphinx': ('http://sphinx-doc.org', None),
}

