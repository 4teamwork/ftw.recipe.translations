from StringIO import StringIO
from ftw.recipe.translations import discovery
from ftw.recipe.translations.i18ntools import rebuild_pot
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
    for group in discovery.discover(sources_directory):
        if not group['pot']:
            continue

        if group['package'] != group['domain']:
            continue

        locales = os.path.join(sources_directory, group['package'],
                               group['locales'])
        package_dir = os.path.join(sources_directory, group['package'])
        sourcedir = './' + os.path.relpath(
            os.path.abspath(os.path.join(locales, '..')),
            package_dir)
        potpath = os.path.join(package_dir, group['pot'])

        manual = ''
        if group['manual']:
            manual = os.path.join(package_dir, group['manual'])

        rebuild_pot(package_dir, sourcedir, group['domain'], potpath, manual)
