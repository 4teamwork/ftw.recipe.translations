from ftw.recipe.translations import loader
from ftw.recipe.translations import writer
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from unittest import TestCase
import os.path


class TestPofileRegistry(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.tempdir = self.layer[u'tempdir']

    def test_finds_pofile_paths(self):
        fshelpers.create_structure(self.tempdir, {
            'pyfoo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                'foo-de.po')})
        catalog = loader.load_translation_catalog(self.tempdir)
        message, = catalog.messages
        registry = writer.PofileRegistry(self.tempdir)

        expected = os.path.join(self.tempdir,
                                'pyfoo/foo/locales/de/LC_MESSAGES/foo.po')
        self.assertEqual(expected,
                          registry.find_pofile_path_for(message, 'de'))

    def test_caches_pofiles(self):
        fshelpers.create_structure(self.tempdir, {
            'pyfoo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                'foo-de.po')})
        catalog = loader.load_translation_catalog(self.tempdir)
        message, = catalog.messages
        registry = writer.PofileRegistry(self.tempdir)

        self.assertIs(registry.find_pofile_for(message, 'de'),
                      registry.find_pofile_for(message, 'de'),
                      'Pofiles should be cached')


class TestWriter(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.tempdir = self.layer[u'tempdir']

    def test_updating_existing_messages(self):
        fshelpers.create_structure(self.tempdir, {
            'pyfoo/foo/locales/foo.pot': fshelpers.asset('foo.pot'),
            'pyfoo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                'foo-de.po')})

        catalog = loader.load_translation_catalog(self.tempdir)
        message = catalog.get_message('pyfoo', 'foo', 'Login')
        message.translate('de', 'Einloggen')

        writer.write_catalog(self.tempdir, catalog)

        pofile = fshelpers.cat(self.tempdir,
                               'pyfoo/foo/locales/de/LC_MESSAGES/foo.po')

        self.assertIn(
            b'\n'.join((b'msgid "Login"',
                        b'msgstr "Einloggen"')),
            pofile)

    def test_removes_language_code_and_name(self):
        # In Plone, the language is defined through the location of the
        # pofile, e.g. it is obvious that locales/de/LC_MESSAGES/foo.po is
        # a German translation.
        # We therefore do not include the language-code and language-name
        # headers in the po file and remove them when i18ndude adds them,
        # so that they are no longer wrong..

        fshelpers.create_structure(self.tempdir, {
            'pyfoo/foo/locales/foo.pot': fshelpers.asset('foo.pot'),
            'pyfoo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                'foo-de.po')})

        catalog = loader.load_translation_catalog(self.tempdir)
        writer.write_catalog(self.tempdir, catalog)
        pofile = fshelpers.cat(self.tempdir,
                               'pyfoo/foo/locales/de/LC_MESSAGES/foo.po')

        lines = pofile.split(b'\n')
        self.assertEqual([b'"Language-Team: LANGUAGE <LL@li.org>\\n"'],
                          [line for line in lines if line.startswith(b'"Lang')])

    def test_removes_domain(self):
        # In Plone, the domain is defined through the basename of the
        # pofile. The "Domain:" header is not necessary, so we remove it.

        fshelpers.create_structure(self.tempdir, {
            'pyfoo/foo/locales/foo.pot': fshelpers.asset('foo.pot'),
            'pyfoo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                'foo-de.po')})

        catalog = loader.load_translation_catalog(self.tempdir)
        writer.write_catalog(self.tempdir, catalog)
        pofile = fshelpers.cat(self.tempdir,
                               'pyfoo/foo/locales/de/LC_MESSAGES/foo.po')

        lines = pofile.split(b'\n')
        self.assertEqual([],
                          [line for line in lines if line.startswith(b'"Domain')])
