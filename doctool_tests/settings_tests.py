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
import os
import sys
import logging
import unittest
import unittest.mock as mock

from doctool import settings


class SettingsTests(unittest.TestCase):

    @mock.patch('os.path.abspath')
    def test_normpath(self, mocked_abspath):
        windows_path = r'C:\my\windows\path'
        mocked_abspath.return_value = windows_path
        normed_path = settings.normpath(windows_path)

        mocked_abspath.assert_called_once_with(windows_path)
        self.assertEqual(normed_path, windows_path.replace('\\', '/'))

    @mock.patch('os.path.join')
    @mock.patch('doctool.settings.normpath')
    def test_absjoin(self, mocked_normpath, mocked_join):
        elements = (r'C:\my\windows\path', 'in', 'file', 'system',)
        expected_joined_path = '/'.join(elements)
        mocked_join.return_value = '\\'.join(elements)
        mocked_normpath.return_value = expected_joined_path
        joined_path = settings.absjoin(*elements)

        mocked_join.assert_called_once_with(*elements)
        mocked_normpath.assert_called_once_with(mocked_join.return_value)

        self.assertEqual(joined_path, expected_joined_path)

    def test_defined_constants(self):
        constant_names = (
                ('REPO_BASE', 1),
                ('TEMPLATES_DIR', 1),
                ('DOCTOOL_ROOTDIR', 1),

                ('DEFAULT_CONFIG', 0),
                ('DOCUMENTATION_REPO', 0),
                ('DEFAULT_OUTPUT_DIRNAME', 0),
                ('DEFAULT_OUTPUT_LOG_FILENAME', 0),
        )

        for (attr, isdir) in constant_names:
            value = getattr(settings, attr)
            self.assertIsNotNone(value)
            if isdir:
                self.assertTrue(os.path.isdir(value))

        self.assertEqual(settings.DEFAULT_VERSION, '0.0.0.0')
        self.assertEqual(settings.IS_WINDOWS, sys.platform == 'win32')
        self.assertEqual(settings.DEFAULT_HOST, '(127.0.0.1|localhost)')

        self.assertEqual(settings.DOCTOOL_GLOBAL_LOGGING_LEVEL, logging.DEBUG)
        self.assertDictEqual(settings.DOCTOOL_GLOBAL_LOGGING_LEVELS, {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        })
