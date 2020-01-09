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
:summary: This module implements custom Sphinx Directive, to download inline binary file

.. download-inline:: uri

    Text to display
"""
from docutils import nodes
from docutils.parsers.rst import Directive


class DownloadInlineDirective(Directive):
    """Directive to download inline binary file such as PDF."""
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    option_spec = {}

    def _process_raw(self):
        """
        Process RAW output

        :return: The processed node(s)
        :rtype: list
        """
        attributes = {'format': 'html'}
        text = str(self.content[0]).strip()
        uri = str(self.arguments[0]).strip()
        html = '<p><a href="javascript:download_file(\'{0}\', \'{1}\')">{1}</a></p>'.format(uri, text)
        raw_node = nodes.raw(html, html, **attributes)
        raw_node.source, raw_node.line = self.state_machine.get_source_and_line(self.lineno)

        return [raw_node]

    def run(self):
        """
        Entry point

        :return: The processed node(s)
        :rtype: list
        """
        self.assert_has_content()
        return self._process_raw()


def setup(app, **options):
    """
    Override

    :param app: The Sphinx application reference
    :param options: Any extra keyword options
    """
    app.add_directive('download-inline', DownloadInlineDirective)
