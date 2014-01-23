from ftw.recipe.translations import loader
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from unittest2 import TestCase


class TestLoader(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def test_loading_package_translations(self):
        fshelpers.create_structure(self.layer[u'tempdir'], {
                'pyfoo/foo/locales/foo.pot': fshelpers.asset('foo.pot'),
                'pyfoo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                    'foo-de.po')})

        catalog = loader.load_translation_catalog(self.layer[u'tempdir'])
        self.assertEquals(1, len(catalog.messages),
                          'Expected catalog to have one message')

        message, = catalog.messages
        self.assertEquals('pyfoo', message.package)
        self.assertEquals('foo', message.domain)
        self.assertEquals('Login', message.msgid)
        self.assertEquals(None, message.default)
        self.assertEquals({'de': 'Anmelden'}, message.translations)
