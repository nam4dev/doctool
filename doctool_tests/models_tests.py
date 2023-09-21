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
import unittest
import unittest.mock as mock

from doctool_tests.common import Helper
from doctool.models import Theme
from doctool.models import RSTProject
from doctool.models import CodeProject
from doctool.helpers import Types


class ThemeTests(unittest.TestCase):

    def test_attributes(self):
        expected_attributes = dict(
            one='one',
            test='test',
        )
        theme = Theme(**expected_attributes)

        for k, v in expected_attributes.items():
            self.assertEqual(getattr(theme, k), v)


class RSTProjectTests(unittest.TestCase):

    @classmethod
    def create_project(cls, mocked_load, **options):
        return Helper.create_project(mocked_load, project_class=RSTProject, **options)

    @mock.patch('doctool.partials.os.path.isdir')
    @mock.patch('doctool.partials.os.path.exists')
    @mock.patch('doctool.models.RSTProject.load')
    @mock.patch('doctool.models.RSTProject.build_toctree')
    def test_build(self, mocked_build_toctree, mocked_load, mocked_exists, mocked_isdir):
        dir2parse = '/documentation/path'
        project, manager, configuration = self.create_project(mocked_load, dir2parse=dir2parse)

        mocked_isdir.return_value = True
        mocked_exists.return_value = True

        project.build()

        mocked_build_toctree.assert_called_once_with(project.src_dirname)

    @mock.patch('doctool.partials.os.path.isdir')
    @mock.patch('doctool.partials.os.path.exists')
    @mock.patch('doctool.models.RSTProject.load')
    def test_teardown(self, mocked_load, mocked_exists, mocked_isdir):
        dir2parse = '/documentation/path'
        project, manager, configuration = self.create_project(mocked_load, dir2parse=dir2parse)
        manager.configure_mock(garbage=[])
        mocked_isdir.return_value = True
        mocked_exists.return_value = True

        self.assertNotIn(project.conf_filename, manager.garbage)
        project.teardown()
        self.assertIn(project.conf_filename, manager.garbage)


class CodeProjectTests(unittest.TestCase):

    @classmethod
    def create_project(cls, mocked_load, **options):
        return Helper.create_project(mocked_load, project_class=CodeProject, **options)

    def test_format_heading(self):
        lf = '\n'
        heading = 'My Heading'
        heading_count = len(heading)
        for level, symbol in enumerate(CodeProject.HEADING_LEVELS):
            underlining = symbol * heading_count
            self.assertEqual(
                CodeProject.format_heading(level + 1, heading),
                '{0}{2}{1}{2}{2}'.format(heading, underlining, lf)
            )

    def test_format_heading_with_anchor_text(self):
        lf = '\n'
        heading = 'My Heading'
        heading_count = len(heading)
        for level, symbol in enumerate(CodeProject.HEADING_LEVELS):
            anchor_txt = ''
            heading_level = level + 1
            underlining = symbol * heading_count
            if heading_level == 1:
                anchor_txt += '.. _{0}: {1}{1}'.format(heading, lf)

            self.assertEqual(
                CodeProject.format_heading(heading_level, heading, anchor=1),
                '{3}{0}{2}{1}{2}{2}'.format(heading, underlining, lf, anchor_txt)
            )

    @mock.patch('doctool.models.os.path.getsize')
    def test_skip(self, mocked_getsize):
        expected_module = 'module'
        mocked_getsize.return_value = 6
        self.assertFalse(CodeProject.skip(expected_module))
        mocked_getsize.assert_called_once_with(expected_module)

        mocked_getsize.return_value = 2
        self.assertTrue(CodeProject.skip(expected_module))

    def test_makename(self):
        package, module, sub = 'srcpackage', 'module', 'src'
        name = CodeProject.makename(package, module, sub=sub)
        self.assertEqual(name, 'package.module')

        package, module, sub = '.srcpackage', 'module', 'src'
        name = CodeProject.makename(package, module, sub=sub)
        self.assertEqual(name, 'package.module')

    @mock.patch('doctool.partials.os.path.isdir')
    @mock.patch('doctool.partials.os.path.exists')
    @mock.patch('doctool.models.CodeProject.load')
    def test_ctor(self, mocked_load, mocked_exists, mocked_isdir):
        dir2parse = '/src/path'
        project, manager, configuration = self.create_project(mocked_load, dir2parse=dir2parse)

        self.assertEqual(project.notoc, project.configuration.get('nottoc', False))
        self.assertEqual(project.master_doc, project.configuration.get('master_doc', 'index'))
        self.assertEqual(project.output_dir, '')
        self.assertEqual(project.api_options, project.configuration.get('api_options', CodeProject.API_OPTIONS))

        data = Types.AttributeDict(
            dict(
                uid=project.id,
                project_name=project.name,
                master_doc='index',
                html_static_paths=[],
                output_dir=project.helper.absjoin(manager.output_dir, project.id),
                source_dir=project.src_dirname,
                output_format=project._output_format,
                extra_paths=project.extra_paths,
                metadata=project.metadata,
                theme=project.theme
            )
        )
        expected_data = data.copy()
        expected_data['VERSION'] = '1.0.0.0'
        expected_data['master_title'] = 'master_title'
        expected_data['dirs2append'] = []

        data_context_builder = mock.Mock(return_value=expected_data)
        manager.configure_mock(data_context_builder=data_context_builder)

        mocked_isdir.return_value = True
        mocked_exists.return_value = True

        self.assertDictEqual(project.data, expected_data)
        manager.data_context_builder.assert_called_once_with(**data)
