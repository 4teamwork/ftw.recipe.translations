from ftw.recipe.translations import loader
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from unittest import TestCase


class TestLoader(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.tempdir = self.layer[u'tempdir']

    def test_loading_package_translations(self):
        fshelpers.create_structure(self.tempdir, {
                'pyfoo/foo/locales/foo.pot': fshelpers.asset('foo.pot'),
                'pyfoo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                    'foo-de.po')})

        catalog = loader.load_translation_catalog(self.layer[u'tempdir'])
        self.assertEqual(1, len(catalog.messages),
                          'Expected catalog to have one message')

        message, = catalog.messages
        self.assertEqual('pyfoo', message.package)
        self.assertEqual('foo', message.domain)
        self.assertEqual('Login', message.msgid)
        self.assertEqual(None, message.default)
        self.assertEqual({'de': 'Anmelden'}, message.translations)
