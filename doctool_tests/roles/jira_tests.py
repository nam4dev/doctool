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

from docutils import nodes
from doctool.roles import jira


class JIRATests(unittest.TestCase):

    def _assert_reference_node(self, node, type_, jira_uri, slug):
        self.assertIsInstance(node, nodes.reference)
        self.assertEqual(node.astext(), 'JIRA {} {}'.format(type_.capitalize(), slug))
        self.assertEqual(node.attributes['refuri'], '{}/{}'.format(jira_uri, slug))

    def test_jira_role_base(self):
        slug = 'ISSUE-1'
        type_ = 'issue'
        options = {'classes': ['link']}
        jira_uri = 'https://jira.com'

        app_config = mock.Mock(jira_project_url=jira_uri)
        app = mock.Mock(config=app_config)
        env = mock.Mock(app=app)
        settings = mock.Mock(env=env)
        document = mock.Mock(settings=settings)
        inliner = mock.Mock(document=document)

        [node], [] = jira.role_base(None, '', slug, 0, inliner, options=options, role_type=type_)

        self._assert_reference_node(node, type_, jira_uri, slug)

    def test_jira_role_base_invalid_id(self):
        slug = 'ISSUE-0'
        lineno = 0
        expected_prb = 'PRB'
        expected_error = 'Test Error Message'
        error = mock.Mock(return_value=expected_error)
        problematic = mock.Mock(return_value=expected_prb)
        reporter = mock.Mock(error=error)
        inliner = mock.Mock(reporter=reporter, problematic=problematic)

        [prb], [msg] = jira.role_base(None, '', slug, lineno, inliner, options={})

        problematic.assert_called_once()
        error.assert_called_once_with('JIRA ID number must be a number greater than or equal to 1; '
                                      '"{0}" is invalid.'.format(slug), line=lineno)

        self.assertEqual(prb, expected_prb)
        self.assertEqual(msg, expected_error)

    @mock.patch('doctool.roles.jira.role_base')
    def test_jira_issue_role(self, mocked_role_base):
        slug = 'ISSUE-1'
        lineno = 0
        expected_node = nodes.reference()
        mocked_role_base.return_value = [expected_node], []
        inliner = mock.Mock()
        options = {}

        [node], [] = jira.issue_role(None, '', slug, lineno, inliner, options=options)

        mocked_role_base.assert_called_once_with(
            None, '', slug, lineno, inliner, options=options, content=None
        )

        self.assertIs(node, expected_node)

    @mock.patch('doctool.roles.jira.role_base')
    def test_jira_story_role(self, mocked_role_base):
        slug = 'ISSUE-1'
        lineno = 0
        expected_node = nodes.reference()
        mocked_role_base.return_value = [expected_node], []
        inliner = mock.Mock()
        options = {}

        [node], [] = jira.story_role(None, '', slug, lineno, inliner, options=options)

        mocked_role_base.assert_called_once_with(
            None, '', slug, lineno, inliner, role_type='story', options=options, content=None
        )

        self.assertIs(node, expected_node)

    def test_make_link_node(self):
        slug = 'ISSUE-1'
        type_ = 'issue'
        options = {'classes': ['link']}
        jira_uri = 'https://jira.com'
        app_config = mock.Mock(jira_project_url=jira_uri)
        app = mock.Mock(config=app_config)

        node = jira.make_link_node('', app, type_, slug, options)
        self._assert_reference_node(node, type_, jira_uri, slug)

    def test_make_link_node_no_jira_project_url_defined(self):
        jira_uri = ''
        app_config = mock.Mock(jira_project_url=jira_uri)
        app = mock.Mock(config=app_config)

        with self.assertRaises(ValueError) as ctx:
            jira.make_link_node('', app, '', '', {})

        self.assertEqual(str(ctx.exception), 'jira_project_url configuration value is not set (Empty Value)')
