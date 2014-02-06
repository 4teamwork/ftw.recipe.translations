from ftw.recipe.translations.i18ntools import rebuild_package_potfiles
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from ftw.recipe.translations.tests import pohelpers
from unittest2 import TestCase


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
        rebuild_package_potfiles(self.tempdir, 'foo')
        self.assertEquals({'Foo': ''}, pohelpers.messages(*potfile))

    def test_does_not_rebuild_secondary_domain_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/bar.pot': fshelpers.asset('empty.pot')})

        potfile = (self.tempdir, 'foo/foo/locales/bar.pot')
        self.assertEquals({}, pohelpers.messages(*potfile))
        rebuild_package_potfiles(self.tempdir, 'foo')
        self.assertEquals({}, pohelpers.messages(*potfile))

    def test_merges_manual_pot_files(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot'),
                'foo/foo/locales/foo-manual.pot': fshelpers.asset(
                    'foo.pot'),
                })

        rebuild_package_potfiles(self.tempdir, 'foo')
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

        rebuild_package_potfiles(self.tempdir, 'foo')
        pofile = (self.tempdir, 'foo/foo/locales/foo.pot')
        self.assertEquals({'Foo': '',
                           'Login': ''}, pohelpers.messages(*pofile))

    def test_path_comments_are_relative_in_potfile(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/foo/__init__.py': '_("Foo")',
                'foo/foo/locales/foo.pot': fshelpers.asset('empty.pot')})

        potfile = (self.tempdir, 'foo/foo/locales/foo.pot')
        self.assertEquals({}, pohelpers.messages(*potfile))
        rebuild_package_potfiles(self.tempdir, 'foo')
        self.assertEquals({'Foo': ['./foo/foo/__init__.py:1']},
                          pohelpers.message_references(*potfile))
