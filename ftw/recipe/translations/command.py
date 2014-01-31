from ftw.recipe.translations import sync
from ftw.recipe.translations import upload
from pkg_resources import get_distribution
import argparse
import sys


def version():
    return get_distribution('ftw.recipe.translations').version


def main(sources_dir, spreadsheet_url):
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('--version', action='version',
                        version='%%(prog)s %s' % version())
    parser.add_argument('--sources', '-s',
                        metavar='src-directory',
                        dest='sources_dir',
                        help='Path to the sources directory.',
                        default=sources_dir)

    subparsers = parser.add_subparsers(help='Actions', dest='action')
    sync.setup_argparser(subparsers)
    upload.setup_argparser(subparsers)

    args = parser.parse_args()
    args.func(args, spreadsheet_url)
