from gspread import Client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.keyring_storage import Storage
import httplib2
import oauth2client.tools
import os
import os.path


SCOPE = 'http://spreadsheets.google.com/feeds/'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


class Connector(object):

    def __call__(self):
        return self.connect(self.get_credentials())

    def get_credentials(self):
        storage = Storage('ftw.recipe.translations', os.getlogin())
        credentials = storage.get()

        if credentials and not credentials.invalid:
            return credentials

        if credentials and credentials.invalid:
            credentials.refresh(httplib2.Http())
            return storage.get()

        return self.authorize(storage)

    def authorize(self, storage):
        client_secret_path = self.get_client_secret_json_path()
        flow = flow_from_clientsecrets(client_secret_path,
                                       scope=SCOPE,
                                       redirect_uri=REDIRECT_URI)
        flags = oauth2client.tools.argparser.parse_args([])
        return oauth2client.tools.run_flow(flow, storage, flags)

    def get_client_secret_json_path(self):
        path = os.path.expanduser('~/.buildout/ftw.recipe.translations.json')
        if os.path.exists(path):
            return path

        print 'The clients scretes file for the Google Application is missing at ', \
            path
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

    def connect(self, credentials):
        client = Client(None)
        credentials.apply(client.session.headers)
        return client
