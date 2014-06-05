from ftw.recipe.translations.masstranslate import download
from ftw.recipe.translations.masstranslate import sync
from ftw.recipe.translations.masstranslate import upload
from ftw.recipe.translations.utils import version
import argparse
import sys


def main(spreadsheet_url, sources_dir):
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('--version', action='version',
                        version='%%(prog)s %s' % version())
    parser.add_argument('--sources', '-s',
                        metavar='src-directory',
                        dest='sources_dir',
                        help='Path to the sources directory.',
                        default=sources_dir)
    parser.add_argument('--noauth_local_webserver',
                        default=False,
                        type=bool,
                        help='Set this option to true if you do not have a browser on the computer you are running this script'
                        )

    subparsers = parser.add_subparsers(help='Actions', dest='action')
    sync.setup_argparser(subparsers)
    upload.setup_argparser(subparsers)
    download.setup_argparser(subparsers)

    args = parser.parse_args()
    args.func(args, spreadsheet_url)
