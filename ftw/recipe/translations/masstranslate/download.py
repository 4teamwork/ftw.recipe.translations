from __future__ import print_function
from ftw.recipe.translations.google import Spreadsheet
from ftw.recipe.translations.loader import load_translation_catalog
from ftw.recipe.translations.writer import write_catalog
from six.moves import input
import sys


def setup_argparser(subparsers):
    subparser = subparsers.add_parser('download', help=download.__doc__)
    subparser.set_defaults(func=download_command)


def download_command(args, spreadsheet_url):
    spreadsheet = Spreadsheet(
        noauth_local_webserver=args.noauth_local_webserver
    )
    spreadsheet.connect()
    spreadsheet.open(spreadsheet_url)
    return download(spreadsheet, args.sources_dir)


def download(spreadsheet, sources_directory, worksheet_name=None,
             languages=None):
    """Download translations from the configured spreadsheet and merge them
    into the .po-files in the sources directory.
    """

    if worksheet_name is None:
        worksheet_name = select_worksheet(spreadsheet)

    data = spreadsheet.download(worksheet_name)
    if languages is None:
        languages = select_languages(data)

    catalog = load_translation_catalog(sources_directory)
    for row in data:
        msg = catalog.get_message(
            package=row.get('package'),
            domain=row.get('domain'),
            msgid=row.get('id'))

        for lang in languages:
            if not row['translations'].get(lang, None):
                continue
            msgstr = row['translations'][lang]
            msg.translate(lang, msgstr)

    write_catalog(sources_directory, catalog)

    return data


def select_worksheet(spreadsheet, stdout=sys.stdout):
    print('Please select a worksheet to download:', file=stdout)
    names = spreadsheet.worksheets()
    for num, name in enumerate(names, start=1):
        print('[%i] %s' % (num, name), file=stdout)
    print('', file=stdout)

    while True:
        try:
            num = int(input('Please enter the spreadsheet number: '))
            return names[num - 1]
        except (ValueError, IndexError):
            continue


def select_languages(data, stdout=sys.stdout):
    available_languages = set()
    for item in data:
        available_languages.update(list(item.get('translations', {}).keys()))

    print('Please select the languages to synchronize:', file=stdout)
    for lang in sorted(available_languages):
        print('- %s' % lang, file=stdout)

    print('', file=stdout)
    print('Enter one language code at a time, finish ' + \
        'selection with an empty enter.', file=stdout)

    languages = []
    while True:
        input = input('Language: ').strip()
        if not input and len(languages) == 0:
            print('Please select at least one language.', file=stdout)
        elif not input:
            break
        elif input in available_languages:
            languages.append(input)
        else:
            print('The language "%s" cannot be selected.' % input, file=stdout)

    return languages
