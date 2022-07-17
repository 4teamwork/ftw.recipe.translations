from __future__ import print_function
from ftw.recipe.translations.google import Spreadsheet
from ftw.recipe.translations.loader import load_translation_catalog
from ftw.recipe.translations.utils import capture_streams
from six.moves import filter
from io import BytesIO
import sys


def setup_argparser(subparsers):
    subparser = subparsers.add_parser('upload', help=upload.__doc__)
    subparser.set_defaults(func=upload_command)

    subparser.add_argument(
        'languages', nargs='*', metavar='lang',
        help='Languages which should be translated. Messages translated'
        ' into all of theese languages are skipped unless the --all  flag'
        ' is used.')

    subparser.add_argument(
        '--all', '-a', action='store_false',
        dest='filter_translated',
        help='By default messages translated into all translated languages'
        ' are filtered because they are already translated. When using this'
        ' flag, all messages are included even when translated completely.')

    subparser.add_argument(
        '--additional-languages', '-l', nargs='*',
        metavar='lang',
        dest='additional_languages',
        help='Additional list of languages to be uploaded. Theese languages'
        ' are not checked for existing translations. See the --all flag for'
        ' details.')


def upload_command(args, spreadsheet_url):
    print('Spreadsheet:', spreadsheet_url)
    spreadsheet = Spreadsheet(
        noauth_local_webserver=args.noauth_local_webserver
    )
    spreadsheet.connect()
    spreadsheet.open(spreadsheet_url)
    return upload(spreadsheet, args.sources_dir,
                  languages=args.languages,
                  filter_translated=args.filter_translated,
                  additional_languages=args.additional_languages)


def upload(spreadsheet, sources_directory, languages=None,
           additional_languages=None, filter_translated=True,
           output=sys.stdout):
    """Upload the translations into the configured spreadsheet in a
    new worksheet.
    """
    include_languages = (languages or []) + (additional_languages or [])
    if len(include_languages) == 0:
        include_languages = None

    with capture_streams(stdout=output or BytesIO()):
        print('Loading translations')
        catalog = load_translation_catalog(sources_directory)

        data = catalog.get_message_dicts(include_languages)
        if filter_translated:
            data = list(filter(translated_languages_filterer(languages or None),
                               data))

        data.sort(key=lambda item: (item.get('package'),
                                    item.get('domain'),
                                    item.get('msgid')))

        worksheet_title = spreadsheet.upload(data)
        print('Uploaded into worksheet "%s"' % worksheet_title)


def translated_languages_filterer(languages):
    def _filterer(item):
        langs = languages or list(item['translations'].keys())
        for lang in langs:
            if not item['translations'].get(lang, None):
                return True
        return False
    return _filterer
