import unittest.mock as mock

from doctool.helpers import Types
from doctool.helpers import ProjectHelper
from doctool.interfaces import IManager


class Helper:
    """
    Class grouping some testing utilities to factorize behavior
    """

    @classmethod
    def create_project(cls, mocked_load,
                       project_class=None,
                       dir2parse='/documentation/path', slugify=None, normpath=None):
        manager = mock.Mock(spec=IManager)
        configuration = mock.Mock()

        mocked_absjoin = mock.Mock()
        mocked_absjoin.return_value = 'REPO{}'.format(dir2parse)

        slugify = slugify or (lambda x: x.replace(' ', '-'))
        normpath = normpath or (lambda x: x.replace('\\', '/'))

        manager.configure_mock(
            theme='bootstrap',
            helper=mock.Mock(
                spec=ProjectHelper,
                absjoin=mocked_absjoin,
                normpath=normpath,
                slugify=slugify),
            output_format='html'
        )

        mocked_load.return_value = Types.AttributeDict(dict(
            api=0,
            rank=0,
            name='test_doc',
            metadata={},
            dir2parse=dir2parse,
        ))

        return project_class(manager, configuration), manager, configuration
