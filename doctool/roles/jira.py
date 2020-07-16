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
:summary: Defines Custom JIRA Sphinx roles

Usage :

    In your RST file, add this role as following :

    :jira_issue:`PROJECT-ID` => jira_base_uri + PROJECT-ID
    :jira_story:`PROJECT-ID` => jira_base_uri + PROJECT-ID
"""
from docutils import nodes
from docutils.parsers.rst.roles import set_classes


def role_base(name, rawtext, text, lineno, inliner, options=None, content=None, role_type='issue'):
    """Link to a JIRA issue.

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.
    Both are allowed to be empty.

    :param role_type: The role type
    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    options = options or {}
    try:
        project, jira_id = text.split('-')
        jira_id = int(jira_id)
        if jira_id <= 0:
            raise ValueError
    except ValueError:
        msg = inliner.reporter.error(
            'JIRA ID number must be a number greater than or equal to 1; '
            '"{0}" is invalid.'.format(text), line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    app = inliner.document.settings.env.app
    node = make_link_node(rawtext, app, role_type, text, options)
    return [node], []


def issue_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """Link to a JIRA issue.

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.
    Both are allowed to be empty.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    return role_base(name, rawtext, text, lineno, inliner,
                     options=options, content=content)


def story_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """Link to a JIRA issue.

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.
    Both are allowed to be empty.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """
    return role_base(name, rawtext, text, lineno, inliner,
                     options=options, content=content, role_type='story')


def make_link_node(rawtext, app, type_, slug, options):
    """Create a link to a JIRA resource.

    :param rawtext: Text being replaced with link node.
    :param app: Sphinx application context
    :param type_: Link type_ (issue, etc.)
    :type slug: str
    :param slug: ID of the thing to link to
    :param options: Options dictionary passed to role func.
    """
    try:
        base = app.config.jira_project_url
        if not base:
            raise AttributeError('Empty Value')
    except AttributeError as err:
        raise ValueError('jira_project_url configuration value is not set ({0})'.format(err))

    node = ""
    if type_ in ('issue', 'story'):
        if not str(base).endswith('/'):
            base += '/'
        ref = base + slug
        set_classes(options)
        node = nodes.reference(
            rawtext, 'JIRA {0} {1}'.format(type_.capitalize(), slug.upper()), refuri=ref, **options
        )

    return node
