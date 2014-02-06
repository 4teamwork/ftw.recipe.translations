from StringIO import StringIO
from ftw.recipe.translations import inflator
from ftw.recipe.translations.i18ntools import rebuild_package_potfiles
from ftw.recipe.translations.i18ntools import sync_pofiles
from ftw.recipe.translations.utils import capture_streams
from ftw.recipe.translations.utils import find_package_directory
from ftw.recipe.translations.utils import version
import argparse
import os
import sys


def main(buildout_dir, package_name, i18n_domain, package_namespace, package_dir):
    assert buildout_dir, 'missing compulsory argument buildout_dir'
    assert package_name, 'missing compulsory argument package_name'

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('--version', action='version',
                        version='%%(prog)s %s' % version())
    parser.add_argument('new_languages', nargs='*')
    arguments = parser.parse_args()

    new_languages = arguments.new_languages or []

    if not i18n_domain:
        i18n_domain = package_name
    if not package_dir:
        package_dir = find_package_directory(buildout_dir, package_name,
                                             package_namespace)

    package_root = buildout_dir
    build_translations(package_dir, package_root, i18n_domain, new_languages)


def build_translations(package_dir, package_root, i18n_domain,
                       new_languages=None, output=sys.stdout):
    with capture_streams(stdout=output or StringIO()):
        rebuild_inflator(package_dir, i18n_domain)
        rebuild_package_potfiles(package_root, package_dir, i18n_domain)
        sync_pofiles(package_dir, new_languages)


def rebuild_inflator(package_dir, i18n_domain):
    potfile_name = '{}-content.pot'.format(i18n_domain)
    potfile = os.path.join(package_dir, 'locales', potfile_name)
    inflator.rebuild_pot(potfile, package_dir, i18n_domain)
