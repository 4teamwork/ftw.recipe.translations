from StringIO import StringIO
from ftw.recipe.translations.i18nbuild.command import build_translations
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from ftw.recipe.translations.tests import pohelpers
from unittest2 import TestCase
import os.path


class TestI18nbuildCommand(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.tempdir = self.layer[u'tempdir']

    def test_rebuilds_primary_domain_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot')})

        potfile = (self.tempdir, 'foo/foo/locales/foo.pot')
        self.assertEquals({}, pohelpers.messages(*potfile))
        build_translations(self.tempdir, self.tempdir, 'foo', output=None)
        self.assertEquals({'Foo': ''}, pohelpers.messages(*potfile))

    def test_does_not_rebuild_secondary_domain_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/bar.pot': fshelpers.asset('empty.pot')})

        potfile = (self.tempdir, 'foo/foo/locales/bar.pot')
        self.assertEquals({}, pohelpers.messages(*potfile))
        build_translations(self.tempdir, self.tempdir, 'foo', output=None)
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

        build_translations(self.tempdir, self.tempdir, 'foo', output=None)
        pofile = (self.tempdir, 'foo/foo/locales/de/LC_MESSAGES/foo.po')
        self.assertEquals({'Foo': '',
                           'Login': ''}, pohelpers.messages(*pofile))

    def test_merges_content_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot'),
                'foo/foo/locales/foo-content.pot': fshelpers.asset(
                    'foo.pot'),
                'foo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                    'empty.po'),
                })

        build_translations(self.tempdir, self.tempdir, 'foo', output=None)
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
        build_translations(self.tempdir, self.tempdir, 'foo', output=output)

        self.assertEquals({'Foo': ''}, pohelpers.messages(*pofile))
        self.assertRegexpMatches(output.getvalue(),
                                 r'\/foo.po: 1 added, 0 removed')

    def test_creates_selected_languages_when_missing(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/locales/bar.pot': fshelpers.asset('foo.pot')})

        enpath = os.path.join(self.tempdir,
                              'foo/foo/locales/en/LC_MESSAGES/bar.po')

        build_translations(self.tempdir, self.tempdir, 'foo', output=None)
        self.assertFalse(os.path.exists(enpath),
                         'A sync without selecting languages should'
                         ' not create new languages.')

        build_translations(self.tempdir, self.tempdir, 'foo', new_languages=['en'], output=None)
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

        build_translations(self.tempdir, self.tempdir, 'foo', new_languages=['de'], output=None)

        self.assertItemsEqual(
            ['foo/foo/__init__.py',
             'foo/foo/locales/foo.pot',
             'foo/foo/locales/foo-manual.pot',
             'foo/foo/locales/de/LC_MESSAGES/foo.po'],
            fshelpers.files(self.tempdir))

    def test_path_comments_are_relative_in_potfile(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot')})

        potfile = (self.tempdir, 'foo/foo/locales/foo.pot')
        self.assertEquals({}, pohelpers.messages(*potfile))
        build_translations(self.tempdir, self.tempdir, 'foo', output=None)
        self.assertEquals({'Foo': ['./foo/foo/__init__.py:1']},
                          pohelpers.message_references(*potfile))

    def test_path_comments_are_relative_in_pofile(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot'),
                'foo/foo/locales/de/LC_MESSAGES/foo.po': fshelpers.asset(
                    'empty.po'),
                })


        pofile = (self.tempdir, 'foo/foo/locales/de/LC_MESSAGES/foo.po')
        build_translations(self.tempdir, self.tempdir, 'foo', output=None)
        self.assertEquals({'Foo': ['./foo/foo/__init__.py:1']},
                          pohelpers.message_references(*pofile))

    def test_synced_files_have_no_Domain_header(self):
        package = (self.tempdir, 'foo/foo')
        locales = (package, 'locales')
        locales_de = (locales, 'de/LC_MESSAGES')
        fshelpers.create_structure({
                (package, '__init__.py'): '_("Foo")',
                (locales, 'foo.pot'): fshelpers.asset('empty.pot'),
                (locales_de, 'foo.po'): fshelpers.asset('empty.po')})

        build_translations(self.tempdir, self.tempdir, 'foo', output=None)

        self.assertNotIn(
            'Domain',
            pohelpers.headers(locales_de, 'foo.po'),

            'The "Domain" header is not necessary for Plone, since the'
            ' filename contains the domain and it  is often not set'
            ' correctly, therefore we remove  it.')

        self.assertNotIn(
            'Domain',
            pohelpers.headers(locales, 'foo.pot'),

            'The "Domain" header is not necessary for Plone, since the'
            ' filename contains the domain and it  is often not set'
            ' correctly, therefore we remove  it.')

    def test_synced_files_have_no_Language_Code_header(self):
        package = (self.tempdir, 'foo/foo')
        locales = (package, 'locales')
        locales_de = (locales, 'de/LC_MESSAGES')
        fshelpers.create_structure({
                (package, '__init__.py'): '_("Foo")',
                (locales, 'foo.pot'): fshelpers.asset('empty.pot'),
                (locales_de, 'foo.po'): fshelpers.asset('empty.po')})

        build_translations(self.tempdir, self.tempdir, 'foo', output=None)

        self.assertNotIn(
            'Language-Code',
            pohelpers.headers(locales_de, 'foo.po'),

            'The "Language-Code" header is not necessary for Plone, since the'
            ' filename contains the domain and it  is often not set'
            ' correctly, therefore we remove  it.')

        self.assertNotIn(
            'Language-Code',
            pohelpers.headers(locales, 'foo.pot'),

            'The "Language-Code" header is not necessary for Plone, since the'
            ' filename contains the domain and it  is often not set'
            ' correctly, therefore we remove  it.')

    def test_synced_files_have_no_Language_Name_header(self):
        package = (self.tempdir, 'foo/foo')
        locales = (package, 'locales')
        locales_de = (locales, 'de/LC_MESSAGES')
        fshelpers.create_structure({
                (package, '__init__.py'): '_("Foo")',
                (locales, 'foo.pot'): fshelpers.asset('empty.pot'),
                (locales_de, 'foo.po'): fshelpers.asset('empty.po')})

        build_translations(self.tempdir, self.tempdir, 'foo', output=None)

        self.assertNotIn(
            'Language-Name',
            pohelpers.headers(locales_de, 'foo.po'),

            'The "Language-Code" header is not necessary for Plone, since the'
            ' filename contains the domain and it  is often not set'
            ' correctly, therefore we remove  it.')

        self.assertNotIn(
            'Language-Name',
            pohelpers.headers(locales, 'foo.pot'),

            'The "Language-Code" header is not necessary for Plone, since the'
            ' filename contains the domain and it  is often not set'
            ' correctly, therefore we remove  it.')
