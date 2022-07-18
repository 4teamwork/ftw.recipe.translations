from ftw.recipe.translations.testing import MASSTRANSLATE_RECIPE_FIXTURE
from unittest import TestCase
import os


DEFAULT_BUILDOUT_CONFIG = '\n'.join((
        '[buildout]',
        'parts = translations',
        '',
        '[translations]',
        'recipe = ftw.recipe.translations'))


class TestRecipe(TestCase):

    layer = MASSTRANSLATE_RECIPE_FIXTURE

    def setUp(self):
        self.__dict__.update(self.layer['buildout'])
        self.maxDiff = None

    def test_installing_recipe(self):
        self.write('buildout.cfg', DEFAULT_BUILDOUT_CONFIG)
        output = self.system(self.buildout).strip()
        self.assertRegex(output, r'^Installing translations')
        self.assertRegex(output,
                                 r'Generated script.*bin/masstranslate')

    def test_recipe_creates_translations_script(self):
        self.write('buildout.cfg', DEFAULT_BUILDOUT_CONFIG)
        self.system(self.buildout)
        expected = os.path.join(self.sample_buildout, 'bin', 'masstranslate')
        self.assertTrue(os.path.exists(expected),
                        'Missing executable %s' % expected)

    def test_script_is_executable(self):
        self.write('buildout.cfg', DEFAULT_BUILDOUT_CONFIG)
        self.system(self.buildout)
        path = os.path.join(self.sample_buildout, 'bin', 'masstranslate')
        self.assertTrue(os.access(path, os.X_OK),
                        '%s should be executable' % path)

    def test_source_path_is_passed_as_argument(self):
        self.write('buildout.cfg', DEFAULT_BUILDOUT_CONFIG)
        self.system(self.buildout)
        path = os.path.join(self.sample_buildout, 'bin', 'masstranslate')
        with open(path) as file_:
            script = file_.read()

        self.assertRegex(script, 'sources_dir = ".*src"')

    def test_spreadshet_configurable(self):
        url = 'https://docs.google.com/spreadsheet/ccc?key=adsf123adsf'
        self.write('buildout.cfg', '\n'.join((
                    DEFAULT_BUILDOUT_CONFIG,
                    'spreadsheet = %s' % url)))
        self.system(self.buildout)
        path = os.path.join(self.sample_buildout, 'bin', 'masstranslate')
        with open(path) as file_:
            script = file_.read()

        self.assertIn('spreadsheet = "%s"' % url, script)

    def test_spreadsheet_is_None_by_default(self):
        self.write('buildout.cfg', DEFAULT_BUILDOUT_CONFIG)
        self.system(self.buildout)
        path = os.path.join(self.sample_buildout, 'bin', 'masstranslate')
        with open(path) as file_:
            script = file_.read()

        self.assertIn('spreadsheet = None', script)
