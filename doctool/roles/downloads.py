#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Namgyal BRISSON (nam4dev)"
__since__ = "01/09/2020"
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
:summary: Defines Custom Download Inline roles

Usage :

    In your RST file, add this role as following :

    :download-inline:`uri,text` => create a JS link with text & URI
"""
from docutils import nodes


def download_inline_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """Create a JS link to ensure the file opens properly on click.

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
    try:
        uri, content = [a.strip() for a in text.split(',')]
    except ValueError:
        msg = inliner.reporter.error(
            'Download Inline seems malformed; '
            '"{0}" is invalid.'.format(text), line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    attributes = {'format': 'html'}
    html = '<a href="javascript:download_file(\'{0}\', \'{1}\')">{1}</a>'.format(uri, content)
    raw_node = nodes.raw(html, html, **attributes)
    return [raw_node], []
