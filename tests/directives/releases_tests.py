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
import json
import jinja2
import unittest
import unittest.mock as mock

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import DirectiveError

from doctool.directives import releases


class ReleasesDirectiveTests(unittest.TestCase):

    @classmethod
    def create_directive(cls, name='releases', arguments=None, options=None, content='', lineno=0,
                         content_offset=None, block_text='', state=None, state_machine=None):
        options = options or {}
        arguments = arguments or []

        return releases.ReleasesDirective(name, arguments, options, content, lineno,
                                          content_offset, block_text, state, state_machine)

    def setUp(self):
        self.directive = self.create_directive()

    def tearDown(self):
        self.directive = None

    def test_properties(self):
        self.assertEqual(self.directive.has_content, True)
        self.assertEqual(self.directive.required_arguments, 1)
        self.assertEqual(self.directive.optional_arguments, 1)
        self.assertEqual(self.directive.final_argument_whitespace, True)
        self.assertDictEqual(self.directive.option_spec, {
            'format': directives.unchanged
        })

    def test_ctor(self):
        self.assertIsInstance(self.directive._jinja2_env, jinja2.Environment)

    @mock.patch('doctool.directives.releases.ReleasesDirective._get_releases_info')
    def test__template2output(self, mocked__get_releases_info):
        content = [
            '<h1>My Super Title</h1>\n',
            '{% for item in items %}<p>{{ item }}</p>\n{% endfor %}',
        ]
        items = [
            'Item {}'.format(i) for i in range(5)
        ]
        fake_path = '/fake/path/to/json/file.json'
        mocked__get_releases_info.return_value = dict(items=items)
        self.directive.content = content
        self.directive.arguments = [fake_path]
        output = self.directive._template2output

        mocked__get_releases_info.assert_called_once_with(fake_path)

        expected_output = '\n'.join((
            '<h1>My Super Title</h1>',
            '',
            '<p>Item 0</p>',
            '<p>Item 1</p>',
            '<p>Item 2</p>',
            '<p>Item 3</p>',
            '<p>Item 4</p>',
            '',
        ))

        self.assertEqual(output, expected_output)

    @mock.patch('doctool.directives.releases.ReleasesDirective._get_releases_info')
    @mock.patch('doctool.directives.releases.jinja2.Environment.from_string')
    def test__template2output_with_error(self, mocked__from_string, *_):
        expected_error = ValueError('Test error')
        template = mock.Mock()
        template.render.side_effect = expected_error
        mocked__from_string.return_value = template
        self.directive.arguments = ['fake_path']

        with self.assertRaises(DirectiveError) as ctx:
            _ = self.directive._template2output

        self.assertEqual(ctx.exception.msg, str(expected_error))

    def test__get_releases_info_invalid_uri(self):
        fake_path = '/fake/path/to/json/file.json'
        expected_error = (
            "Could not reach URI {0} "
            "(Invalid URL '{0}': "
            "No schema supplied. Perhaps you meant http://{0}?)"
        ).format(fake_path)
        with self.assertRaises(DirectiveError) as ctx:
            self.directive._get_releases_info(fake_path)

        self.assertEqual(str(ctx.exception.msg), expected_error)

    def test__get_releases_info_valid_fs_uri(self):
        expected_releases_info = dict(releases=[
            dict(
                date='01-01-2019',
                version='1.0.0.0',
                linux='https://mocked/path/to/linux/binary.run',
                windows='https://mocked/path/to/windows/binary.exe'
            )
        ])
        expected_called_path = '/mocked/path/to/json/file.json'
        with mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(expected_releases_info))) as mock_file:
            releases_info = self.directive._get_releases_info(expected_called_path)
            mock_file.assert_called_once_with(expected_called_path)

        self.assertDictEqual(releases_info, expected_releases_info)

    def test__get_releases_info_invalid_json_content(self):
        expected_called_path = '/mocked/path/to/json/file.json'
        expected_error = (
            '{} is not a valid JSON file (Expecting value: line 1 column 1 (char 0))'
        ).format(expected_called_path)

        with mock.patch("builtins.open", mock.mock_open(read_data='')) as mock_file:
            with self.assertRaises(DirectiveError) as ctx:
                self.directive._get_releases_info(expected_called_path)

            self.assertEqual(str(ctx.exception.msg), expected_error)
            mock_file.assert_called_once_with(expected_called_path)

    @mock.patch('doctool.directives.releases.requests.get')
    def test__get_releases_info_valid_http_uri(self, mocked_get):
        expected_releases_info = dict(releases=[
            dict(
                date='01-01-2019',
                version='1.0.0.0',
                linux='https://mocked/path/to/linux/binary.run',
                windows='https://mocked/path/to/windows/binary.exe'
            )
        ])
        mocked_get.return_value = mock.Mock(json=lambda: expected_releases_info)
        releases_info = self.directive._get_releases_info('https://mocked/path/to/json/file.json')

        self.assertDictEqual(releases_info, expected_releases_info)

    def test__process_rst(self):
        get_source_and_line = (mock.Mock(), 0,)
        self.directive.state_machine = mock.Mock()
        self.directive.state_machine.get_source_and_line.return_value = get_source_and_line
        self.directive.state = mock.Mock()
        self.directive.content = mock.Mock(source='', parent=None, parent_offset='')

        output = '.. important:: whatever'
        children = self.directive._process_rst(output)

        self.assertListEqual(children, [])
        self.directive.state.nested_parse.assert_called_once()
        self.directive.state_machine.get_source_and_line.assert_called_once_with(self.directive.lineno)

    def test__process_rst_with_error(self):
        expected_error = ValueError('An error occurred')
        self.directive.state_machine = mock.Mock()
        self.directive.state_machine.get_source_and_line.side_effect = expected_error

        with self.assertRaises(DirectiveError) as ctx:
            self.directive._process_rst('.. important:: whatever')

        self.assertEqual(str(ctx.exception.msg), str(expected_error))

    def test__process_raw(self):
        output = '<h1>Super Title</h1>'
        get_source_and_line = (mock.Mock(), 0,)
        self.directive.options['format'] = 'html'
        self.directive.state_machine = mock.Mock()
        self.directive.state_machine.get_source_and_line.return_value = get_source_and_line
        children = self.directive._process_raw(output)

        self.assertEqual(len(children), 1)
        node = children[0]
        self.assertIsInstance(node, nodes.raw)
        self.assertTupleEqual((node.source, node.line,), get_source_and_line)
        self.assertEqual(node.astext(), output)

    @mock.patch('doctool.directives.releases.ReleasesDirective._process_rst')
    @mock.patch('doctool.directives.releases.ReleasesDirective.assert_has_content')
    @mock.patch('doctool.directives.releases.ReleasesDirective._template2output', new_callable=mock.PropertyMock)
    def test_run_for_rst_format(self, mocked_output, mocked_assert_has_content, mocked__process_rst):
        expected_output = '{% for item in items %}<p>{{ item }}</p>{% endfor %}'
        mocked_output.return_value = expected_output
        self.directive.options = dict(format='rst')
        self.directive.run()

        mocked_assert_has_content.assert_called_once_with()
        mocked__process_rst.assert_called_once_with(expected_output)

    @mock.patch('doctool.directives.releases.ReleasesDirective._process_raw')
    @mock.patch('doctool.directives.releases.ReleasesDirective.assert_has_content')
    @mock.patch('doctool.directives.releases.ReleasesDirective._template2output', new_callable=mock.PropertyMock)
    def test_run_for_raw_format(self, mocked_output, mocked_assert_has_content, mocked__process_rst):
        expected_output = '<h1>My Super Title</h1>'
        mocked_output.return_value = expected_output
        self.directive.options = dict(format='html')
        self.directive.run()

        mocked_assert_has_content.assert_called_once_with()
        mocked__process_rst.assert_called_once_with(expected_output)

    def test_setup(self):
        app = mock.Mock()
        releases.setup(app)
        app.add_directive.assert_called_once_with('releases', releases.ReleasesDirective)

