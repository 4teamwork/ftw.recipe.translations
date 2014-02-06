from ftw.recipe.translations.inflator import rebuild_pot
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from ftw.recipe.translations.tests import pohelpers
from unittest2 import TestCase
import os.path


class TestRebuildPotCommand(TestCase):

    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.tempdir = self.layer[u'tempdir']

    def test_extract_messages(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/profiles/default/content_creation/content.json':
                        fshelpers.asset('content.json'),
                    })

        rebuild_pot(os.path.join(self.tempdir, 'inflator.pot',),
                    os.path.join(self.tempdir, 'foo', 'foo', 'profiles'),
                    'foo.foo')

        messages = pohelpers.messages(self.tempdir, 'inflator.pot')
        self.assertIn('Foo', messages)


