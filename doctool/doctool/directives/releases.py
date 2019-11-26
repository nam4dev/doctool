__author__ = "Namgyal BRISSON (nam4dev)"
__since__ = "11/25/2019"
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
:summary: This module implements `.. releases: <path_or_url>` custom Sphinx Directive
"""
import json
import jinja2
import requests

from docutils import nodes
from docutils import statemachine
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives


class ReleasesDirective(Directive):
    """Directive to insert release markups into a table.
    It handles whatever it is needed to be rendered

    The releases directive takes as positional & required argument a file path to a JSON file
    It could also be a valid HTTP uri producing expected JSON schema.

    The expected JSON schema could be as needed, there's no constraints!

    For example,

        .. code-block:: json

            {
                "program": "<program name>",
                "releases": [
                    {
                        "version": "1.0.0.0",
                        "date": "01-01-2019",
                        "mac": "https://site.com/mac-release.run",
                        "linux": "https://site.com/linux-release.run",
                        "windows": "https://site.com/windows-release.exe"
                    }
                ]
            }

    An optional argument `:format:` indicates in which format the directive's content is written.

    Supported formats:

        - html
        - rest (rst)
        - any format the `.. raw::` directive takes

    Examples::

        HTML example

        .. releases:: ./release_list.json
            :format: html

            {% for release in release %}

                <h1>{{ release['name'] }}</h1>

                <table class="table">
                    <thead>
                        <tr>
                            <td>Linux</td>
                            <td>Windows</td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>{{ release['linux'] }}</td>
                            <td>{{ release['windows'] }}</td>
                        </tr>
                    </tbody>
                </table>

            {% endfor %}

        RST example

        Generating REST format will allow one to take advantage of REST parser.
        For example, any title will be included into the TOC (represented into the right menu of the document)

        .. releases:: https://wwww.site.com/release_list.json
            :format: rest

            {% macro raw_tag() %}
            .. raw:: html
            {% endmacro %}

            {% macro to_title(release) %}
            {%- set title=release['name'] -%}
            {{ title }}
            {{ '#' * title|length }}
            {% endmacro %}

            {% for release in release %}

            {{ to_title(release) }}
            {{ raw_tag() }}

                <table class="table">
                    <thead>
                        <tr>
                            <td>Linux</td>
                            <td>Windows</td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>{{ release['linux'] }}</td>
                            <td>{{ release['windows'] }}</td>
                        </tr>
                    </tbody>
                </table>

            {% endfor %}
    """
    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True

    option_spec = {
        'format': directives.unchanged
    }

    @property
    def _template2output(self):
        """
        Property getting Jinja template to the converted output

        :return: The converted output
        :rtype: str
        """
        releases_info = self._get_releases_info(self.arguments[0])
        template = self._jinja2_env.from_string('\n'.join(self.content))
        try:
            return template.render(**releases_info)
        except Exception as error:
            raise self.error('%s' % error)

    def __init__(self, name, arguments, options, content, lineno,
                 content_offset, block_text, state, state_machine):
        """
        Override
        Constructor

        Instantiate the Jinja environment instance
        """
        super().__init__(name, arguments, options, content, lineno,
                         content_offset, block_text, state, state_machine)

        self._jinja2_env = jinja2.Environment(loader=jinja2.BaseLoader)

    def _get_releases_info(self, uri):
        """
        Get the releases info from an URI (HTTP or from a path)

        :param uri: The HTTP URL or the local path where JSON data lies
        :type uri: str

        :return: The releases data
        :rtype: dict
        """
        releases_info = {}
        try:
            with open(uri) as fd:
                try:
                    releases_info = json.load(fd)
                except (TypeError, ValueError, Exception) as e:
                    raise self.error('{} is not a valid JSON file ({})'.format(uri, e))
        except (FileNotFoundError, OSError):
            try:
                response = requests.get(uri, verify=False)
                releases_info = response.json()
            except requests.exceptions.RequestException as error:
                raise self.error('Could not reach URI %s (%s)' % (uri, str(error)))

        return releases_info

    def _process_rst(self, output):
        """
        Process an RST output

        :param output: The output to process
        :type output: str

        :return: The processed node(s)
        :rtype: list
        """
        try:
            node = nodes.paragraph()
            node.source, node.line = self.state_machine.get_source_and_line(self.lineno)

            converted = statemachine.StringList(
                initlist=output.split('\n'),
                source=self.content.source,
                parent=self.content.parent,
                parent_offset=self.content.parent_offset,
            )
            self.state.nested_parse(converted, self.content_offset, node, match_titles=True)
        except Exception as error:
            raise self.error('%s' % error)
        return node.children

    def _process_raw(self, output):
        """
        Process an RAW output

        :param output: The output to process
        :type output: str

        :return: The processed node(s)
        :rtype: list
        """
        attributes = {'format': self.options.get('format', 'html')}
        raw_node = nodes.raw('', output, **attributes)
        raw_node.source, raw_node.line = self.state_machine.get_source_and_line(self.lineno)
        return [raw_node]

    def run(self):
        """
        Entry point

        :return: The processed node(s)
        :rtype: list
        """
        self.assert_has_content()

        output = self._template2output
        selected_format = self.options.get('format', 'rst')

        if selected_format in ('rst', 'rest',):
            node_list = self._process_rst(output)
        else:
            node_list = self._process_raw(output)

        return node_list


def setup(app, **options):
    """
    Override

    :param app: The Sphinx application reference
    :param options: Any extra keyword options
    """
    app.add_directive('releases', ReleasesDirective)
