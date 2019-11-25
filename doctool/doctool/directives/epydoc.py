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
:summary: Overloads the plantuml directive, in order to add the `:from_file:` optional attribute.

"""
import re

from sphinx.ext.autodoc import cut_lines

# This part is converting epydoc most common text-mark,
# like @param <name>:, ... into Sphinx ones (:param <name>:)
re_field = re.compile('@(param|type|rtype|return|copyright|organization|author|raise|raises|summary|since)')
re_copyright = re.compile('@copyright')
re_block_type = re.compile('@(note|attention|caution|error)')


def fix_docstring(app, what, name, obj, options, lines):
    """
    Convert Epydoc docstring into Sphinx ones

    :param app: The Sphinx App instance
    :param what:
    :param name:
    :param obj: the object itself
    :param options: Sphinx options
    :param lines: The list of lines
    """
    valid_lines = []
    for i, line in enumerate(lines[:]):
        if re_copyright.match(line):
            valid_lines.append(re_field.sub(r':\1', lines.pop(i)))
            for l in lines:
                if re_field.match(l):
                    valid_lines.append(re_field.sub(r':\1', l))
            break
        if re_field.match(line):
            valid_lines.append(re_field.sub(r':\1', line))
        elif re_block_type.match(line):
            try:
                j = i
                while not re_field.match(lines[:][j]):
                    lines[j] = '   {0}\n'.format(lines[:][j].strip())

                    j += 1
            except IndexError:
                pass
            valid_lines.append(re_block_type.sub(r'.. \1:', line))
        else:
            valid_lines.append(line)

    del lines[:]
    lines.extend(valid_lines)


def setup(app, **options):
    """
    Overriding Public method

    :param app: The Sphinx App instance
    :param options: Extra options
    """
    app.connect('autodoc-process-docstring', fix_docstring)
    app.connect('autodoc-process-docstring', cut_lines(25, what=['module']))
    app.add_description_unit('confval', 'confval',
                             objname='configuration value',
                             indextemplate='pair: %s; configuration value')
