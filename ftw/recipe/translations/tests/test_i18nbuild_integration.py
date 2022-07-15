from __future__ import print_function
from ftw.recipe.translations.testing import RECIPE_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from ftw.recipe.translations.tests import pohelpers
from unittest2 import TestCase
import json
import os.path


BUILDOUT_CONFIG = '\n'.join((
        '[buildout]',
        'parts = i18nbuild',
        '',
        '[i18nbuild]',
        'recipe = ftw.recipe.translations:package',
        'package-name = Package',
        'i18n-domain = package',
        'package-namespace = the.package'))


class TestI18nbuildCommandIntegration(TestCase):

    layer = RECIPE_FIXTURE

    def setUp(self):
        self.__dict__.update(self.layer['buildout'])
        self.maxDiff = None

        self.i18n_build = os.path.join(self.sample_buildout, 'bin', 'i18n-build')

    def test_updating_translations(self):
        self.write('buildout.cfg', BUILDOUT_CONFIG)
        self.system(self.buildout)

        package = 'the/package'
        locales = (package, 'locales')
        locales_de = (locales, 'de/LC_MESSAGES')
        locales_en = (locales, 'en/LC_MESSAGES')
        profile = (package, 'profiles/default')

        fshelpers.create_structure(self.sample_buildout, {
                (locales, 'package.pot'): fshelpers.asset('empty.pot'),
                (locales, 'package-manual.pot'): pohelpers.makepo({
                        'label_login': ('Login', '')}),
                (locales, 'plone.pot'): pohelpers.makepo({
                        'save': ('Save', '')}),
                (locales_de, 'package.po'): (
                    fshelpers.asset('empty.po')),
                (locales_en, 'plone.po'): (
                    fshelpers.asset('empty.po')),

                (package, '__init__.py'): '_("Foo")',
                (profile, 'content_creation/01.json'): json.dumps([
                        {'title:translate(package)': 'ContentPage'}])})

        output = self.system(self.i18n_build + ' de')

        try:
            # pot file building
            self.assertDictContainsSubset(
                {u'label_login': u''},
                pohelpers.messages(locales, 'package.pot'),
                'package-manual.pot was not merged')

            self.assertDictContainsSubset(
                {u'Foo': u''},
                pohelpers.messages(locales, 'package.pot'),
                'Package was not scanned, python file translation missing.')

            self.assertDictContainsSubset(
                {u'ContentPage': u''},
                pohelpers.messages(locales, 'package.pot'),
                'Inflater content creation was not scanned.')

            # po syncing
            self.assertEquals({u'label_login': u'',
                               u'Foo': u'',
                               u'ContentPage': u''},
                              pohelpers.messages(locales_de, 'package.po'),
                              'Default domain ("package") .po-file was not synced.')

            self.assertEquals({u'save': u''},
                              pohelpers.messages(locales_de, 'plone.po'),
                              'Alternate domain ("plone") .po-file was not synced.')

            self.assertEquals({u'save': u''},
                              pohelpers.messages(locales_en, 'plone.po'),
                              'Existing language was not synced.')

            lines = fshelpers.cat(locales_de, 'package.po').split('\n')
            self.assertEquals(
                [],
                [line for line in lines if line.startswith('"Domain')],
                '.po-files should not contain Domain-headers, because'
                ' they are not relevant and often not set correctly.')

            # path comments
            self.assertDictContainsSubset(
                {u'Foo': [u'./the/package/__init__.py:1']},
                pohelpers.message_references(locales, 'package.pot'),
                'Path comments are wrong.')

        except:
            print('-' * 30)
            print(output)
            print('-' * 30)
            raise
