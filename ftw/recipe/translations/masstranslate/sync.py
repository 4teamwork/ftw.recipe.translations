from StringIO import StringIO
from ftw.recipe.translations.i18ntools import rebuild_package_potfiles
from ftw.recipe.translations.i18ntools import sync_pofiles
from ftw.recipe.translations.utils import capture_streams
import os.path
import sys


def setup_argparser(subparsers):
    subparser = subparsers.add_parser('sync', help=synchronize.__doc__)
    subparser.set_defaults(func=synchronize_command)

    subparser.add_argument(
        'languages', nargs='*', metavar='lang',
        help='Language code of languages to synchronize.' + \
            ' If defined, only the defined languages are synchronized' + \
            ' and will be created if missing.')

def synchronize_command(args, spreadsheet_url):
    return synchronize(args.sources_dir, args.languages)


def synchronize(sources_directory, languages=None, output=sys.stdout):
    """Rebuilds .pot-files of the default domain of each package in the
    source directory and syncs all .po-files with the .pot-files of all
    domains in each package.
    """
    with capture_streams(stdout=output or StringIO()):
        rebuild_primary_domain_group_potfiles(sources_directory)
        sync_pofiles(sources_directory, languages)


def rebuild_primary_domain_group_potfiles(sources_directory):
    for package_name in os.listdir(sources_directory):
        package_dir = os.path.join(sources_directory, package_name)
        if os.path.isdir(package_dir):
            # assume primary domain is package name, since we have no
            # possibilities to customize the domain in this environment.
            primary_domain = package_name
            rebuild_package_potfiles(package_dir, primary_domain)
