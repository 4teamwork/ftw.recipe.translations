from ftw.recipe.translations import discovery
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from unittest2 import TestCase


class TestDiscovery(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.maxDiff = None
        self.tempdir = self.layer[u'tempdir']


    def test_discovers_translations_in_locales_directories(self):
        fshelpers.create_structure(self.tempdir, {
                u'foo.bar/foo/bar/locales/en/LC_MESSAGES/foo.bar.po': u'',
                u'foo.bar/foo/bar/locales/de/LC_MESSAGES/foo.bar.po': u'',
                u'foo.bar/foo/bar/locales/foo.bar.pot': u''})


        self.assertItemsEqual(
            [{u'domain': u'foo.bar',
              u'package': u'foo.bar',
              u'locales': u'foo/bar/locales',
              u'pot': u'foo/bar/locales/foo.bar.pot',
              u'manual': None,
              u'languages': {
                        u'de': u'foo/bar/locales/de/LC_MESSAGES/foo.bar.po',
                        u'en': u'foo/bar/locales/en/LC_MESSAGES/foo.bar.po'}}
             ],

            discovery.discover(self.tempdir))

    def test_discovers_multiple_domains_in_same_package(self):
        fshelpers.create_structure(self.tempdir, {
                u'foo/foo/locales/en/LC_MESSAGES/foo.po': u'',
                u'foo/foo/locales/de/LC_MESSAGES/foo.po': u'',
                u'foo/foo/locales/de/LC_MESSAGES/bar.po': u'',
                u'foo/foo/locales/foo.pot': u'',
                u'foo/foo/locales/bar.pot': u'',
                })

        self.assertItemsEqual(
            [{u'domain': u'bar',
              u'package': u'foo',
              u'locales': u'foo/locales',
              u'pot': u'foo/locales/bar.pot',
              u'manual': None,
              u'languages': {
                        u'de': u'foo/locales/de/LC_MESSAGES/bar.po'}},

             {u'domain': u'foo',
              u'package': u'foo',
              u'locales': u'foo/locales',
              u'pot': u'foo/locales/foo.pot',
              u'manual': None,
              u'languages': {
                        u'de': u'foo/locales/de/LC_MESSAGES/foo.po',
                        u'en': u'foo/locales/en/LC_MESSAGES/foo.po'}}],

            discovery.discover(self.tempdir))

    def test_translations_without_pot_file(self):
        fshelpers.create_structure(self.tempdir, {
                u'foo/foo/locales/en/LC_MESSAGES/foo.po': u'',
                })

        self.assertItemsEqual(
            [{u'domain': u'foo',
              u'package': u'foo',
              u'locales': u'foo/locales',
              u'pot': None,
              u'manual': None,
              u'languages': {
                        u'en': u'foo/locales/en/LC_MESSAGES/foo.po'}}],

            discovery.discover(self.tempdir))

    def test_lists_manual_pot_files_in_respective_group(self):
        fshelpers.create_structure(self.tempdir, {
                u'foo/bar/locales/en/LC_MESSAGES/foo.po': u'',
                u'foo/bar/locales/foo.pot': u'',
                u'foo/bar/locales/bar.pot': u'',
                u'foo/bar/locales/foo-manual.pot': u'',
                })

        self.assertItemsEqual(
            [{u'domain': u'foo',
              u'package': u'foo',
              u'locales': u'bar/locales',
              u'pot': u'bar/locales/foo.pot',
              u'manual': u'bar/locales/foo-manual.pot',
              u'languages': {
                        u'en': u'bar/locales/en/LC_MESSAGES/foo.po'}},

             {u'domain': u'bar',
              u'package': u'foo',
              u'locales': u'bar/locales',
              u'pot': u'bar/locales/bar.pot',
              u'manual': None,
              u'languages': {},
              }],

            discovery.discover(self.tempdir))

    def test_i18n_directory_is_not_supported(self):
        fshelpers.create_structure(self.tempdir, {
                u'foo/foo/i18n/foo-de.po': u'',
                })

        self.assertItemsEqual(
            [],

            discovery.discover(self.tempdir))
