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
        self.potfile = os.path.join(self.tempdir, 'inflator.pot')
        self.profiles_dir = os.path.join(self.tempdir, 'foo', 'foo',
                                         'profiles')
        self.domain = 'foo.foo'

    def test_no_potfile_with_missing_profiles_dir(self):
        fshelpers.create_structure(self.tempdir, {'foo/foo/__init__.py': ''})

        rebuild_pot(self.potfile, self.profiles_dir, self.domain)
        self.assertFalse(os.path.exists(self.potfile))

    def test_no_potfile_with_missing_inflator_content(self):
        fshelpers.create_structure(self.tempdir,
                        {os.path.join(self.profiles_dir, 'metadata.xml'): ''})

        rebuild_pot(self.potfile, self.profiles_dir, self.domain)
        self.assertFalse(os.path.exists(self.potfile))

    def test_no_potfile_with_missing_translations(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/profiles/default/content_creation/content.json':
                        fshelpers.asset('untranslated_content.json'),
                    })

        rebuild_pot(self.potfile, self.profiles_dir, self.domain)

        self.assertFalse(os.path.exists(self.potfile))

    def test_extract_messages(self):
        potfile = os.path.join(self.tempdir, 'somedir', 'inflator.pot')
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/profiles/default/content_creation/content.json':
                        fshelpers.asset('translated_content.json'),
                    })
        self.assertFalse(os.path.exists(os.path.dirname(potfile)))

        rebuild_pot(potfile, self.profiles_dir, self.domain)

        self.assertTrue(os.path.exists(os.path.dirname(potfile)))
        messages = pohelpers.messages(potfile)
        self.assertTrue(os.path.exists(potfile))
        self.assertIn('Foo', messages)

