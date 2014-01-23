from ftw.recipe.translations import loader
from ftw.recipe.translations import writer
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from unittest2 import TestCase
import os.path



class TestPofileRegistry(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def test_finds_pofile_paths(self):
        fshelpers.create_structure(self.layer[u'tempdir'], {
                'pyfoo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                    'foo-de.po')})
        catalog = loader.load_translation_catalog(self.layer[u'tempdir'])
        message, = catalog.messages
        registry = writer.PofileRegistry(self.layer['tempdir'])

        expected = os.path.join(self.layer['tempdir'],
                                'pyfoo/foo/locales/de/LC_MESSAGES/foo.po')
        self.assertEquals(expected,
                          registry.find_pofile_path_for(message, 'de'))

    def test_caches_pofiles(self):
        fshelpers.create_structure(self.layer[u'tempdir'], {
                'pyfoo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                    'foo-de.po')})
        catalog = loader.load_translation_catalog(self.layer[u'tempdir'])
        message, = catalog.messages
        registry = writer.PofileRegistry(self.layer['tempdir'])

        self.assertIs(registry.find_pofile_for(message, 'de'),
                      registry.find_pofile_for(message, 'de'),
                      'Pofiles should be cached')


class TestWriter(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def test_updating_existing_messages(self):
        fshelpers.create_structure(self.layer[u'tempdir'], {
                'pyfoo/foo/locales/foo.pot': fshelpers.asset('foo.pot'),
                'pyfoo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                    'foo-de.po')})

        catalog = loader.load_translation_catalog(self.layer[u'tempdir'])
        message = catalog.get_message('pyfoo', 'foo', 'Login')
        message.translate('de', 'Einloggen')

        writer.write_catalog(self.layer['tempdir'], catalog)

        pofile = fshelpers.cat(self.layer['tempdir'],
                               'pyfoo/foo/locales/de/LC_MESSAGES/foo.po')

        self.assertIn(
            '\n'.join(('msgid "Login"',
                       'msgstr "Einloggen"')),
            pofile)
