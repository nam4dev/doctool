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

from tests.common import Helper

from doctool import settings
from doctool.helpers import Types
from doctool.partials import PartialProject


class PartialProjectTests(unittest.TestCase):

    @classmethod
    def create_project(cls, mocked_load, **options):
        return Helper.create_project(mocked_load, project_class=PartialProject, **options)

    @mock.patch('doctool.partials.os.path.isdir')
    @mock.patch('doctool.partials.os.path.exists')
    @mock.patch('doctool.partials.PartialProject.load')
    def test_ctor(self, mocked_load, mocked_exists, mocked_isdir):
        dir2parse = '/documentation/path'
        joined_dir2parse = 'REPO{}'.format(dir2parse)
        project, manager, configuration = self.create_project(mocked_load, dir2parse=dir2parse)

        self.assertIs(project.manager, manager)
        self.assertIsNot(project.configuration, configuration)

        self.assertEqual(project.rank, 0)
        self.assertEqual(project.is_api, 0)
        self.assertEqual(project.name, 'test_doc')
        self.assertEqual(project.id, 'documentation-path')
        self.assertFalse(project.dryrun)
        self.assertEqual(project._default_uid, 'documentation-path')
        self.assertEqual(project.slug, 'test_doc')
        self.assertEqual(project.suffix, 'rst')
        self.assertEqual(project.override, 1)
        self.assertIsNone(project.toctree)
        self.assertListEqual(project.extra_paths, [])
        self.assertDictEqual(project.metadata, Types.AttributeDict())
        self.assertEqual(project.first_link, '')

        mocked_exists.return_value = False

        self.assertEqual(project._dir_source, dir2parse)
        manager.helper.absjoin.assert_called_once_with(settings.REPO_BASE, dir2parse)

        mocked_isdir.return_value = True
        mocked_exists.return_value = True

        self.assertEqual(project.src_dirname, joined_dir2parse)
        self.assertEqual(project._dir_source, joined_dir2parse)
        self.assertEqual(project.conf_filename, joined_dir2parse)

    @mock.patch('doctool.partials.PartialProject.load')
    def test_str_repr(self, mocked_load):
        dir2parse = '/documentation/path'
        project, *_ = self.create_project(mocked_load, dir2parse=dir2parse)

        def to_string():
            string = u''
            for attr, value in project.__dict__.items():
                if not attr.startswith('__'):
                    string += u'{0} : {1}\n'.format(attr, value)
            return string

        self.assertEqual(str(project), to_string())

    @mock.patch('doctool.partials.os.path.isdir')
    @mock.patch('doctool.partials.os.path.exists')
    @mock.patch('doctool.partials.PartialProject.load')
    def test_data(self, mocked_load, mocked_exists, mocked_isdir):
        dir2parse = '/documentation/path'
        project, manager, configuration = self.create_project(mocked_load, dir2parse=dir2parse)

        mocked_isdir.return_value = True
        mocked_exists.return_value = True

        data = dict(
            uid=project.id,
            project_name=project.name,
            master_doc='index',
            output_dir=project.helper.absjoin(manager.output_dir, project.id),
            source_dir=project.src_dirname,
            output_format=project._output_format,
            extra_paths=project.extra_paths,
            metadata=project.metadata,
            theme=project.theme
        )
        expected_data = data.copy()
        expected_data['VERSION'] = '1.0.0.0'
        expected_data['master_title'] = 'master_title'

        data_context_builder = mock.Mock(return_value=expected_data)
        manager.configure_mock(data_context_builder=data_context_builder)

        self.assertDictEqual(project.data, expected_data)
        manager.data_context_builder.assert_called_once_with(**data)

    @mock.patch('doctool.partials.os.path.isfile')
    @mock.patch('doctool.partials.PartialProject.load')
    def test_build_toctree(self, mocked_load, mocked_isfile):
        dir2parse = '/documentation/path'
        mocked_isfile.return_value = True
        project, manager, configuration = self.create_project(mocked_load, dir2parse=dir2parse)

        with mock.patch("builtins.open", mock.mock_open(read_data='.. toctree:\n\n\tanother')) as mock_file:
            project.build_toctree(dir2parse)

        self.assertListEqual(project.toctree, [
            {
                'children': [],
                'hash': 0,
                'link': 'documentation-path/another.html',
                'name': '@doctool.missing.title',
                'alias': ''
            }
        ])

    @mock.patch('doctool.partials.ProjectHelper.load_from_file')
    def test_load(self, mocked_load_from_file):
        expected_conf = {
            'MAXDEPTH': 5,
            'GRAPHVIZ': {}
        }
        expected_loaded_conf = expected_conf.copy()
        expected_loaded_conf['api'] = 1

        mocked_load_from_file.return_value = expected_loaded_conf

        self.assertDictEqual(PartialProject.load(expected_conf), expected_loaded_conf)
        mocked_load_from_file.assert_called_once_with(expected_conf)
