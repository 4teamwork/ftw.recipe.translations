from ftw.recipe.translations.masstranslate import download
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from ftw.recipe.translations.tests import pohelpers
from io import StringIO
from unittest import TestCase
from unittest.mock import patch


class SpreadSheetMock(object):

    def __init__(self, worksheets):
        self._worksheets = worksheets

    def worksheets(self):
        return sorted(self._worksheets.keys())

    def download(self, worksheet_title):
        return self._worksheets.get(worksheet_title)


class TestDownload(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.tempdir = self.layer[u'tempdir']

    def test_download(self):
        from ftw.recipe.translations.masstranslate import download
        fshelpers.create_structure(self.tempdir, {
            'foo/bar/locales/bar.pot': fshelpers.asset('empty.pot'),
            'foo/bar/locales/de/LC_MESSAGES/bar.po': pohelpers.makepo({
                'label_login': ('Login', '')})})
        pofile = (self.tempdir, 'foo/bar/locales/de/LC_MESSAGES/bar.po')

        self.assertEqual({'label_login': ''},
                         pohelpers.messages(*pofile))

        spreadsheet = SpreadSheetMock(
            {'worksheet': [{'package': u'foo',
                            'domain': u'bar',
                            'id': u'label_login',
                            'default': u'Login',
                            'translations': {u'de': u'Anmelden'},
                            },
                           {'package': u'foo',
                            'domain': u'bar',
                            'id': u'this_was_removed',
                            'default': u'Yay',
                            'translations': {u'de': u'Yay'},
                            }]})
        download.download(spreadsheet, self.tempdir,
                          worksheet_name='worksheet',
                          languages=['de'])

        self.assertEqual({'label_login': 'Anmelden'},
                         pohelpers.messages(*pofile))

    def test_only_selected_languages_are_synced(self):
        from ftw.recipe.translations.masstranslate import download
        fshelpers.create_structure(self.tempdir, {
            'foo/bar/locales/bar.pot': fshelpers.asset('empty.pot'),
            'foo/bar/locales/de/LC_MESSAGES/bar.po': pohelpers.makepo({
                'label_login': ('Login', 'de original')}),
            'foo/bar/locales/fr/LC_MESSAGES/bar.po': pohelpers.makepo({
                'label_login': ('Login', 'fr original')})})
        de_pofile = (self.tempdir, 'foo/bar/locales/de/LC_MESSAGES/bar.po')
        fr_pofile = (self.tempdir, 'foo/bar/locales/fr/LC_MESSAGES/bar.po')

        spreadsheet = SpreadSheetMock(
            {'worksheet': [{'package': u'foo',
                            'domain': u'bar',
                            'id': u'label_login',
                            'default': u'Login',
                            'translations': {u'de': u'Anmelden',
                                             u'fr': u'Connecter'},
                            }]})
        download.download(spreadsheet, self.tempdir,
                          worksheet_name='worksheet',
                          languages=['de'])

        self.assertEqual({'label_login': 'Anmelden'},
                         pohelpers.messages(*de_pofile))
        self.assertEqual({'label_login': 'fr original'},
                         pohelpers.messages(*fr_pofile))

    def test_download_does_not_empty_existing_translations(self):
        from ftw.recipe.translations.masstranslate import download
        fshelpers.create_structure(self.tempdir, {
            'foo/bar/locales/bar.pot': fshelpers.asset('empty.pot'),
            'foo/bar/locales/de/LC_MESSAGES/bar.po': pohelpers.makepo({
                'label_login': ('Login', 'Anmelden')})})
        pofile = (self.tempdir, 'foo/bar/locales/de/LC_MESSAGES/bar.po')

        spreadsheet = SpreadSheetMock(
            {'worksheet': [{'package': u'foo',
                            'domain': u'bar',
                            'id': u'label_login',
                            'default': u'Login',
                            'translations': {u'de': u''},
                            }]})
        download.download(spreadsheet, self.tempdir,
                          worksheet_name='worksheet',
                          languages=['de'])

        self.assertEqual({'label_login': 'Anmelden'},
                         pohelpers.messages(*pofile))


class TestDownloadInteractiveSelections(TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    def test_interactive_select_worksheet(self, mock_stdout):
        spreadsheet = SpreadSheetMock({'foo': '',
                                       'bar': '',
                                       'baz': ''})

        with patch('builtins.input', side_effect=['2']):
            self.assertEqual(
                'baz',
                download.select_worksheet(spreadsheet, stdout=mock_stdout))
            self.assertEqual(
                [
                    'Please select a worksheet to download:',
                    '[1] bar',
                    '[2] baz',
                    '[3] foo',
                    '',
                    '',
                ],
                mock_stdout.getvalue().split('\n'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_interactive_select_worksheet_bad_input(self, mock_stdout):
        spreadsheet = SpreadSheetMock({'foo': '',
                                       'bar': ''})

        with patch('builtins.input', side_effect=['foo', '', '3', '1']):
            self.assertEqual(
                'bar',
                download.select_worksheet(spreadsheet, stdout=mock_stdout))

            self.assertEqual(
                [
                    'Please select a worksheet to download:',
                    '[1] bar',
                    '[2] foo',
                    '',
                    '',
                ],
                mock_stdout.getvalue().split('\n'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_interactive_select_languages(self, mock_stdout):
        data = [{'package': u'foo',
                 'domain': u'bar',
                 'id': u'label_login',
                 'default': u'Login',
                 'translations': {u'fr': u'Connecter'},
                 },
                {'package': u'foo',
                 'domain': u'bar',
                 'id': u'label_logout',
                 'default': u'Logout',
                 'translations': {u'de': u'Abmelden'},
                 }]

        with patch('builtins.input', side_effect=['fr', 'de', '', ]):
            self.assertEqual(['fr', 'de'],
                             download.select_languages(data, stdout=mock_stdout))

            self.assertEqual(
                [
                    'Please select the languages to synchronize:',
                    '- de',
                    '- fr',
                    '',
                    ('Enter one language code at a time, finish '
                     'selection with an empty enter.'),
                    ''
                ],
                mock_stdout.getvalue().split('\n'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_interactive_select_languages_bad_input(self, mock_stdout):
        data = [{'package': u'foo',
                 'domain': u'bar',
                 'id': u'label_login',
                 'default': u'Login',
                 'translations': {u'fr': u'Connecter'},
                 },
                {'package': u'foo',
                 'domain': u'bar',
                 'id': u'label_logout',
                 'default': u'Logout',
                 'translations': {u'de': u'Abmelden'},
                 }]

        with patch('builtins.input', side_effect=['', 'en', 'de', '']):
            self.assertEqual(['de'],
                             download.select_languages(data, stdout=mock_stdout))

            self.assertEqual(
                [
                    'Please select the languages to synchronize:',
                    '- de',
                    '- fr',
                    '',
                    ('Enter one language code at a time, finish '
                     'selection with an empty enter.'),
                    'Please select at least one language.',
                    'The language "en" cannot be selected.',
                    ''
                ],
                mock_stdout.getvalue().split('\n'))
