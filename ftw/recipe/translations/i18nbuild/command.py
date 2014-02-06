from ftw.recipe.translations.i18ntools import rebuild_package_potfiles
from ftw.recipe.translations.utils import find_package_dir
from ftw.recipe.translations.utils import version
import argparse
import sys
from ftw.recipe.translations import discovery
from ftw.recipe.translations.discovery import discover_package
import os
from ftw.recipe.translations import inflator


def main(buildout_dir, package_name, i18n_domain, package_namespace,
         package_dir):
    assert buildout_dir, 'missing compulsory argument buildout_dir'
    assert package_namespace, 'missing compulsory argument package_namespace'

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('--version', action='version',
                        version='%%(prog)s %s' % version())
    parser.add_argument('new_languages', nargs='*')
    arguments = parser.parse_args()

    new_languages = arguments.languages or []

    if not i18n_domain:
        i18n_domain = package_namespace
    if not package_name:
        package_name = package_namespace
    if not package_dir:
        package_dir = find_package_dir(buildout_dir, package_name)

    build_translations(package_dir, i18n_domain, new_languages)


def build_translations(package_dir, i18n_domain, new_languages=None):
    rebuild_inflator(package_dir, i18n_domain)
    rebuild_package_potfiles(package_dir, i18n_domain)
    sync_potfiles(package_dir, new_languages)


def rebuild_inflator(package_dir, i18n_domain):
    potfile_name = '{}-content.pot'.format(i18n_domain)
    potfile = os.path.join(package_dir, 'locales', potfile_name)
    inflator.rebuild_pot(potfile, package_dir, i18n_domain)


def sync_potfiles(package_dir, new_languages=None):
    pass

