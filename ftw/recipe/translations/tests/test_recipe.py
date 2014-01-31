from ftw.recipe.translations.testing import RECIPE_FIXTURE
from unittest2 import TestCase
import os


DEFAULT_BUILDOUT_CONFIG = '\n'.join((
        '[buildout]',
        'parts = translations',
        '',
        '[translations]',
        'recipe = ftw.recipe.translations'))


I18N_BUILDOUT_CONFIG = '\n'.join((
        '[buildout]',
        'parts = i18n',
        '',
        '[i18n]',
        'recipe = ftw.recipe.translations'))



class TestRecipe(TestCase):

    layer = RECIPE_FIXTURE

    def setUp(self):
        self.__dict__.update(self.layer['buildout'])
        self.maxDiff = None

    def test_installing_recipe(self):
        self.write('buildout.cfg', DEFAULT_BUILDOUT_CONFIG)
        output = self.system(self.buildout).strip()
        self.assertRegexpMatches(output, r'^Installing translations')
        self.assertRegexpMatches(output,
                                 r'Generated script.*bin/translations')

    def test_recipe_creates_translations_script(self):
        self.write('buildout.cfg', DEFAULT_BUILDOUT_CONFIG)
        self.system(self.buildout)
        expected = os.path.join(self.sample_buildout, 'bin', 'translations')
        self.assertTrue(os.path.exists(expected),
                        'Missing executable %s' % expected)

    def test_script_is_executable(self):
        self.write('buildout.cfg', DEFAULT_BUILDOUT_CONFIG)
        self.system(self.buildout)
        path = os.path.join(self.sample_buildout, 'bin', 'translations')
        self.assertTrue(os.access(path, os.X_OK),
                        '%s should be executable' % path)

    def test_source_path_is_passed_as_argument(self):
        self.write('buildout.cfg', DEFAULT_BUILDOUT_CONFIG)
        self.system(self.buildout)
        path = os.path.join(self.sample_buildout, 'bin', 'translations')
        with open(path) as file_:
            script = file_.read()

        self.assertRegexpMatches(script, 'sources_dir = ".*src"')

    def test_spreadshet_configurable(self):
        url = 'https://docs.google.com/spreadsheet/ccc?key=adsf123adsf'
        self.write('buildout.cfg', '\n'.join((
                    DEFAULT_BUILDOUT_CONFIG,
                    'spreadsheet = %s' % url)))
        self.system(self.buildout)
        path = os.path.join(self.sample_buildout, 'bin', 'translations')
        with open(path) as file_:
            script = file_.read()

        self.assertIn('spreadsheet = "%s"' % url, script)

    def test_spreadsheet_is_None_by_default(self):
        self.write('buildout.cfg', DEFAULT_BUILDOUT_CONFIG)
        self.system(self.buildout)
        path = os.path.join(self.sample_buildout, 'bin', 'translations')
        with open(path) as file_:
            script = file_.read()

        self.assertIn('spreadsheet = None', script)
