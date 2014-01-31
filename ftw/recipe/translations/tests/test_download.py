from ftw.recipe.translations import download
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from ftw.recipe.translations.tests import pohelpers
from mocker import ANY
from mocker import MockerTestCase
from unittest2 import TestCase


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
        fshelpers.create_structure(self.tempdir, {
                'foo/bar/locales/bar.pot': fshelpers.asset('empty.pot'),
                'foo/bar/locales/de/LC_MESSAGES/bar.po': pohelpers.makepo({
                        'label_login': ('Login', '')})})
        pofile = (self.tempdir, 'foo/bar/locales/de/LC_MESSAGES/bar.po')

        self.assertEquals({'label_login': ''},
                          pohelpers.messages(*pofile))

        spreadsheet = SpreadSheetMock(
            {'worksheet': [{'package': u'foo',
                            'domain': u'bar',
                            'id': u'label_login',
                            'default': u'Login',
                            'translations': {u'de': u'Anmelden'},
                            }]})
        download.download(spreadsheet, self.tempdir,
                          worksheet_name='worksheet',
                          languages=['de'])

        self.assertEquals({'label_login': 'Anmelden'},
                          pohelpers.messages(*pofile))

    def test_only_selected_languages_are_synced(self):
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

        self.assertEquals({'label_login': 'Anmelden'},
                          pohelpers.messages(*de_pofile))
        self.assertEquals({'label_login': 'fr original'},
                          pohelpers.messages(*fr_pofile))

    def test_download_does_not_empty_existing_translations(self):
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

        self.assertEquals({'label_login': 'Anmelden'},
                          pohelpers.messages(*pofile))



class TestDownloadInteractiveSelections(MockerTestCase):

    def setUp(self):
        super(TestDownloadInteractiveSelections, self).setUp()
        self.raw_input_mock = self.mocker.replace(raw_input)
        self.expect(self.raw_input_mock(ANY)).throw(
            AssertionError('Unexpected raw_input call')).count(0, None)

    def test_interactive_select_worksheet(self):
        spreadsheet = SpreadSheetMock({'foo': '',
                                       'bar': '',
                                       'baz': ''})

        stdout, expect_print = self.mock_stdout()
        with self.mocker.order():
            expect_print('Please select a worksheet to download:')
            expect_print('[1] bar')
            expect_print('[2] baz')
            expect_print('[3] foo')
            expect_print('')
            self.type_when_asked('2', 'Please enter the spreadsheet number: ')

        self.mocker.replay()
        self.assertEquals(
            'baz',
            download.select_worksheet(spreadsheet, stdout=stdout))

    def test_interactive_select_worksheet_bad_input(self):
        spreadsheet = SpreadSheetMock({'foo': '',
                                       'bar': ''})

        stdout, expect_print = self.mock_stdout()
        with self.mocker.order():
            expect_print('Please select a worksheet to download:')
            expect_print('[1] bar')
            expect_print('[2] foo')
            expect_print('')
            self.type_when_asked('foo',
                                 'Please enter the spreadsheet number: ')
            self.type_when_asked('', 'Please enter the spreadsheet number: ')
            self.type_when_asked('3', 'Please enter the spreadsheet number: ')
            self.type_when_asked('1', 'Please enter the spreadsheet number: ')

        self.mocker.replay()
        self.assertEquals(
            'bar',
            download.select_worksheet(spreadsheet, stdout=stdout))

    def test_interactive_select_languages(self):
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

        stdout, expect_print = self.mock_stdout()
        with self.mocker.order():
            expect_print('Please select the languages to synchronize:')
            expect_print('- de')
            expect_print('- fr')
            expect_print('')
            expect_print('Enter one language code at a time, finish '
                         'selection with an empty enter.')
            self.type_when_asked('fr', 'Language: ')
            self.type_when_asked('de', 'Language: ')
            self.type_when_asked('', 'Language: ')

        self.mocker.replay()
        self.assertEquals(['fr', 'de'],
                          download.select_languages(data, stdout=stdout))

    def test_interactive_select_languages_bad_input(self):
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

        stdout, expect_print = self.mock_stdout()
        with self.mocker.order():
            expect_print('Please select the languages to synchronize:')
            expect_print('- de')
            expect_print('- fr')
            expect_print('')
            expect_print('Enter one language code at a time, finish '
                         'selection with an empty enter.')
            self.type_when_asked('', 'Language: ')
            expect_print('Please select at least one language.')
            self.type_when_asked('en', 'Language: ')
            expect_print('The language "en" cannot be selected.')
            self.type_when_asked('de', 'Language: ')
            self.type_when_asked('', 'Language: ')

        self.mocker.replay()
        self.assertEquals(['de'],
                          download.select_languages(data, stdout=stdout))

    def type_when_asked(self, answer, prompt=ANY):
        self.expect(self.raw_input_mock(prompt)).result(answer)

    def mock_stdout(self):
        stdout = self.mocker.mock()

        def expect_print(*lines):
            for line in lines:
                self.expect(stdout.write(line))
                self.expect(stdout.write('\n'))

        return stdout, expect_print
