from StringIO import StringIO
from ftw.recipe.translations.i18ntools import rebuild_package_potfiles
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from ftw.recipe.translations.tests import pohelpers
from ftw.recipe.translations.utils import capture_streams
from unittest2 import TestCase
import os.path


class TestRebuildPotfiles(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.tempdir = self.layer[u'tempdir']

    def test_rebuilds_primary_domain_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot')})

        potfile = (self.tempdir, 'foo/foo/locales/foo.pot')
        self.assertEquals({}, pohelpers.messages(*potfile))
        rebuild_package_potfiles(self.tempdir, self.tempdir, 'foo')
        self.assertEquals({'Foo': ''}, pohelpers.messages(*potfile))

    def test_does_not_rebuild_secondary_domain_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/bar.pot': fshelpers.asset('empty.pot')})

        potfile = (self.tempdir, 'foo/foo/locales/bar.pot')
        self.assertEquals({}, pohelpers.messages(*potfile))
        rebuild_package_potfiles(self.tempdir, self.tempdir, 'foo')
        self.assertEquals({}, pohelpers.messages(*potfile))

    def test_does_not_include_messages_outside_of_package_dir(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot'),
                'src/bar/__init__.py': '_("Bar")'})

        package_dir = os.path.join(self.tempdir, 'foo')
        potfile = (self.tempdir, 'foo/foo/locales/foo.pot')
        rebuild_package_potfiles(self.tempdir, package_dir, 'foo')
        self.assertNotIn('Bar', pohelpers.messages(*potfile),
                         'Messages from sub-checkouts should not be included.')
        self.assertEquals({'Foo': ''}, pohelpers.messages(*potfile),
                          'Expected translations in package to be discovered.')

    def test_merges_manual_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot'),
                'foo/foo/locales/foo-manual.pot': fshelpers.asset(
                    'foo.pot'),
                })

        rebuild_package_potfiles(self.tempdir, self.tempdir, 'foo')
        pofile = (self.tempdir, 'foo/foo/locales/foo.pot')
        self.assertEquals({'Foo': '',
                           'Login': ''}, pohelpers.messages(*pofile))

    def test_merges_content_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot'),
                'foo/foo/locales/foo-content.pot': fshelpers.asset(
                    'foo.pot'),
                })

        rebuild_package_potfiles(self.tempdir, self.tempdir, 'foo')
        pofile = (self.tempdir, 'foo/foo/locales/foo.pot')
        self.assertEquals({'Foo': '',
                           'Login': ''}, pohelpers.messages(*pofile))

    def test_path_comments_are_relative_in_potfile(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot')})

        potfile = (self.tempdir, 'foo/foo/locales/foo.pot')
        self.assertEquals({}, pohelpers.messages(*potfile))
        rebuild_package_potfiles(self.tempdir, self.tempdir, 'foo')
        self.assertEquals({'Foo': ['./foo/foo/__init__.py:1']},
                          pohelpers.message_references(*potfile))

    def test_i18ndude_SystemExit_is_handled(self):
        # This is quite a "stupid" test:
        # Rebuilding a domain without having any translations makes the internal
        # i18ndude command to perform a system exit.
        # This is really bad, since we are possibly building multiple pot-files
        # and are doing more stuff and should be in control of such things.
        fshelpers.create_structure(self.tempdir, {
                'foo/locales/foo.pot': fshelpers.asset('empty.pot')})
        try:
            with capture_streams(stderr=StringIO()):
                rebuild_package_potfiles(self.tempdir, self.tempdir, 'foo')
        except SystemExit:
            assert False, 'SystemExit leaked from i18ndude while rebuilding pot-files!'
