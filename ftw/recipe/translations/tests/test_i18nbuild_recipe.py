from ftw.recipe.translations.testing import RECIPE_FIXTURE
from unittest2 import TestCase
import os.path
import re


BASE_BUILDOUT_CONFIG = '\n'.join((
        '[buildout]',
        'parts = i18nbuild',
        '',
        '[i18nbuild]',
        'recipe = ftw.recipe.translations:package'))


PACKAGE_BUILDOUT_CONFIG = '\n'.join((
        BASE_BUILDOUT_CONFIG,
        'package-name = my.package'))


def extract_script_arguments(script_path):
    command = 'ftw.recipe.translations.i18nbuild.command.main'
    with open(script_path) as file_:
        script = file_.read()
    xpr = 'sys\.exit\(%s\(([^)]*)\)\)' % re.escape(command)
    match = re.search(xpr, script)
    assert match, 'Could not find command call in script %s \n %s' % (
        script_path, xpr)

    args = match.group(1)
    if len(args) == 0:
        return {}

    result = {}
    for name, value in [arg.split('=') for arg in args.split(',')]:
        name, value = name.strip(), value.strip()
        result[name] = value
    return result


class TestRecipe(TestCase):

    layer = RECIPE_FIXTURE

    def setUp(self):
        self.__dict__.update(self.layer['buildout'])
        self.maxDiff = None

    def test_installing_recipe(self):
        self.write('buildout.cfg', PACKAGE_BUILDOUT_CONFIG)
        output = self.system(self.buildout).strip()
        self.assertRegexpMatches(output, r'^Installing i18nbuild')
        self.assertRegexpMatches(output,
                                 r'Generated script.*bin/i18n-build')

    def test_generates_i18nbuild_script(self):
        self.write('buildout.cfg', PACKAGE_BUILDOUT_CONFIG)
        self.system(self.buildout)
        expected = os.path.join(self.sample_buildout, 'bin', 'i18n-build')
        self.assertTrue(os.path.exists(expected),
                        'Missing executable %s' % expected)

    def test_does_not_generate_masstranslate_script(self):
        self.write('buildout.cfg', PACKAGE_BUILDOUT_CONFIG)
        self.system(self.buildout)
        not_expected = os.path.join(self.sample_buildout, 'bin', 'masstranslate')
        self.assertFalse(os.path.exists(not_expected),
                        'Unexpected script was generated: %s' % not_expected)

    def test_passes_buildout_directory_to_command(self):
        self.write('buildout.cfg', PACKAGE_BUILDOUT_CONFIG)
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'i18n-build')
        self.assertDictContainsSubset(
            {'buildout_directory': '"%s"' % self.sample_buildout},
            extract_script_arguments(script_path))

    def test_passes_package_name_to_command(self):
        self.write('buildout.cfg', PACKAGE_BUILDOUT_CONFIG)
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'i18n-build')
        self.assertDictContainsSubset({'package_name': '"my.package"'},
                                      extract_script_arguments(script_path))

    def test_package_name_is_required(self):
        self.write('buildout.cfg', BASE_BUILDOUT_CONFIG)
        output = self.system(self.buildout).strip()
        self.assertRegexpMatches(output, r'i18nbuild:package-name is required')

    def test_passes_i18ndomain_to_command(self):
        self.write('buildout.cfg', '\n'.join((
                    PACKAGE_BUILDOUT_CONFIG,
                    'i18n-domain = thedomain')))
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'i18n-build')
        self.assertDictContainsSubset({'i18n_domain': '"thedomain"'},
                                      extract_script_arguments(script_path))

    def test_passes_package_namespace_to_command(self):
        self.write('buildout.cfg', '\n'.join((
                    PACKAGE_BUILDOUT_CONFIG,
                    'package-namespace = package')))
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'i18n-build')
        self.assertDictContainsSubset({'package_namespace': '"package"'},
                                      extract_script_arguments(script_path))

    def test_passes_package_directory_to_command(self):
        self.write('buildout.cfg', '\n'.join((
                    PACKAGE_BUILDOUT_CONFIG,
                    'package-directory = src/my/package')))
        self.system(self.buildout)
        script_path = os.path.join(self.sample_buildout, 'bin', 'i18n-build')
        self.assertDictContainsSubset({'package_directory': '"src/my/package"'},
                                      extract_script_arguments(script_path))
