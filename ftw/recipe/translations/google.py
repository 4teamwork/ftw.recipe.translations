from datetime import datetime
from ftw.recipe.translations.progresslogger import ProgressLogger
from gspread import Client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.keyring_storage import Storage
from operator import attrgetter
import httplib2
import itertools
import oauth2client.tools
import os
import os.path
import re


SCOPE = 'http://spreadsheets.google.com/feeds/'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
WORKSHEET_PREFIX_XPR = re.compile(r'^(\d*):')

HEADERS = ('package', 'domain', 'id', 'default')


class Spreadsheet(object):

    def __init__(self):
        self.client = None
        self.document = None

    def connect(self):
        self.client = self._setup_client(self._get_credentials())

    def open(self, url):
        self.document = self.client.open_by_url(url)

    def upload(self, data, print_status=True):
        translation_headers = tuple(set(itertools.chain(*[
                        item.get('translations').keys() for item in data])))
        headers = HEADERS + translation_headers
        cols = len(headers)
        rows = len(data) + 1
        worksheet = self._create_worksheet(rows=rows, cols=cols)

        self._update_row(worksheet, 1, headers)

        for row, item in ProgressLogger('Upload', tuple(enumerate(data))):
            values = []
            for header in headers:
                text = item.get(header, item['translations'].get(header))
                if isinstance(text, str):
                    text = text.decode('utf-8')
                if text is None:
                    text = u''
                values.append(text)

            self._update_row(worksheet, row + 2, values)

        return worksheet.title

    def _update_row(self, worksheet, row_num, values):
        range = 'A%s:%s%s' % (
            row_num,
            chr(64 + len(values)),
            row_num)
        cells = worksheet.range(range)

        for col, text in enumerate(values):
            if isinstance(text, str):
                text = text.decode('utf-8')
            if text is None:
                text = u''
            cells[col].value = text

        worksheet.update_cells(cells)

    def download(self, worksheet_title):
        worksheet = self.document.worksheet(worksheet_title)
        items = []
        for item in worksheet.get_all_records():
            item = item.copy()
            item['translations'] = {}
            for key in set(item.keys()) - set(HEADERS + ('translations',)):
                item['translations'][key] = item[key]
                del item[key]
            items.append(item)
        return items

    def worksheets(self):
        names = filter(WORKSHEET_PREFIX_XPR.match,
                       map(attrgetter('title'), self.document.worksheets()))
        return names

    def _create_worksheet(self, rows, cols):
        prefixes = map(int, map(
                lambda name: WORKSHEET_PREFIX_XPR.match(name).group(1),
                self.worksheets()))
        next_prefix = unicode(max(prefixes or [0]) + 1).rjust(3, '0')
        name = ': '.join((next_prefix, datetime.now().strftime('%Y-%m-%d')))
        return self.document.add_worksheet(name, rows=rows, cols=cols)

    def _get_credentials(self):
        storage = Storage('ftw.recipe.translations', os.getlogin())
        credentials = storage.get()

        if credentials:
            credentials.refresh(httplib2.Http())
            return credentials

        return self._authorize(storage)

    def _authorize(self, storage):
        client_secret_path = self._get_client_secret_json_path()
        flow = flow_from_clientsecrets(client_secret_path,
                                       scope=SCOPE,
                                       redirect_uri=REDIRECT_URI)
        flags = oauth2client.tools.argparser.parse_args([])
        return oauth2client.tools.run_flow(flow, storage, flags)

    def _get_client_secret_json_path(self):
        path = os.path.expanduser('~/.buildout/ftw.recipe.translations.json')
        if os.path.exists(path):
            return path

        print 'The clients scretes file for the Google Application' + \
            ' is missing at ', path
        print ''
        print 'Please copy your company application secrets file to this path.'
        print 'If you or your company has not created an application yet, ', \
            'follow the instructions at ', \
            'https://github.com/4teamwork/ftw.recipe.translations/wiki/' + \
            'Creating-a-Google-OAuth-Application'
        print ''
        while not os.path.exists(path):
            print 'ERROR:', path, 'missing'
            raw_input('Press any key to retry')
        return path

    def _setup_client(self, credentials):
        client = Client(None)
        credentials.apply(client.session.headers)
        return client
