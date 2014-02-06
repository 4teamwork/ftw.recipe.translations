from StringIO import StringIO
from ftw.recipe.translations.masstranslate.sync import synchronize
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from ftw.recipe.translations.tests import pohelpers
from unittest2 import TestCase
import os.path


class TestSyncCommand(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.tempdir = self.layer[u'tempdir']

    def test_rebuilds_primary_domain_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot')})

        potfile = (self.tempdir, 'foo/foo/locales/foo.pot')
        self.assertEquals({}, pohelpers.messages(*potfile))
        synchronize(self.tempdir)
        self.assertEquals({'Foo': ''}, pohelpers.messages(*potfile))

    def test_does_not_rebuild_secondary_domain_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/bar.pot': fshelpers.asset('empty.pot')})

        potfile = (self.tempdir, 'foo/foo/locales/bar.pot')
        self.assertEquals({}, pohelpers.messages(*potfile))
        synchronize(self.tempdir)
        self.assertEquals({}, pohelpers.messages(*potfile))

    def test_merges_manual_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot'),
                'foo/foo/locales/foo-manual.pot': fshelpers.asset(
                    'foo.pot'),
                'foo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                    'empty.po'),
                })

        synchronize(self.tempdir, output=None)
        pofile = (self.tempdir, 'foo/foo/locales/de/LC_MESSAGES/foo.po')
        self.assertEquals({'Foo': '',
                           'Login': ''}, pohelpers.messages(*pofile))



    def test_syncs_po_files_of_existing_languages(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot'),
                'foo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                    'empty.po'),
                })


        pofile = (self.tempdir, 'foo/foo/locales/de/LC_MESSAGES/foo.po')
        self.assertEquals({}, pohelpers.messages(*pofile))

        output = StringIO()
        synchronize(self.tempdir, output=output)

        self.assertEquals({'Foo': ''}, pohelpers.messages(*pofile))
        self.assertRegexpMatches(output.getvalue(),
                                 r'\/foo.po: 1 added, 0 removed')

    def test_syncs_only_selected_languages(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/locales/bar.pot': fshelpers.asset('foo.pot'),
                'foo/foo/locales/en/LC_MESSAGES/bar.po': fshelpers.asset(
                    'empty.po'),
                'foo/foo/locales/de/LC_MESSAGES/bar.po': fshelpers.asset(
                    'empty.po'),
                })

        en = (self.tempdir, 'foo/foo/locales/en/LC_MESSAGES/bar.po')
        de = (self.tempdir, 'foo/foo/locales/de/LC_MESSAGES/bar.po')
        self.assertEquals({}, pohelpers.messages(*en))
        self.assertEquals({}, pohelpers.messages(*de))

        synchronize(self.tempdir, languages=['en'], output=None)

        self.assertEquals({'Login': ''}, pohelpers.messages(*en))
        self.assertEquals({}, pohelpers.messages(*de))

    def test_creates_selected_languages_when_missing(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/locales/bar.pot': fshelpers.asset('foo.pot')})

        enpath = os.path.join(self.tempdir,
                              'foo/foo/locales/en/LC_MESSAGES/bar.po')

        synchronize(self.tempdir, output=None)
        self.assertFalse(os.path.exists(enpath),
                         'A sync without selecting languages should'
                         ' not create new languages.')

        synchronize(self.tempdir, languages=['en'], output=None)
        self.assertTrue(os.path.exists(enpath),
                        'A sync with selecting languages should'
                        ' create missing languages.')

        self.assertEquals({'Login': ''}, pohelpers.messages(enpath))

    def test_does_not_sync_manual_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot'),
                'foo/foo/locales/foo-manual.pot': fshelpers.asset(
                    'empty.pot'),
                'foo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                    'foo-de.po'),
                })

        synchronize(self.tempdir, languages=['de'], output=None)

        self.assertItemsEqual(
            ['foo/foo/__init__.py',
             'foo/foo/locales/foo.pot',
             'foo/foo/locales/foo-manual.pot',
             'foo/foo/locales/de/LC_MESSAGES/foo.po'],
            fshelpers.files(self.tempdir))
