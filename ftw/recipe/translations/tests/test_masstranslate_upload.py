from ftw.recipe.translations.masstranslate import upload
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.tests import fshelpers
from ftw.recipe.translations.tests import pohelpers
from unittest2 import TestCase


class SpreadSheetMock(object):

    def __init__(self):
        self.uploaded = None

    def upload(self, data, print_status=True):
        self.uploaded = data


class TestUploadCommand(TestCase):
    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.tempdir = self.layer[u'tempdir']

    def test_upload_messages(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/bar/locales/bar.pot': fshelpers.asset('empty.pot'),
                'foo/bar/locales/de/LC_MESSAGES/bar.po': pohelpers.makepo({
                        'label_login': ('Login', 'Anmelden')}),
                'foo/bar/locales/fr/LC_MESSAGES/bar.po': pohelpers.makepo({
                        'label_login': ('Login', 'Connecter')})})

        spreadsheet = SpreadSheetMock()
        upload.upload(spreadsheet, self.tempdir, filter_translated=False,
                      output=None)
        self.assertEquals([{'package': u'foo',
                            'domain': u'bar',
                            'id': u'label_login',
                            'default': u'Login',
                            'translations': {u'de': u'Anmelden',
                                             u'fr': u'Connecter'},
                            }],
                          spreadsheet.uploaded)

    def test_only_upload_selected_languages(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/bar/locales/bar.pot': fshelpers.asset('empty.pot'),
                'foo/bar/locales/de/LC_MESSAGES/bar.po': pohelpers.makepo({
                        'label_login': ('Login', 'Anmelden')}),
                'foo/bar/locales/fr/LC_MESSAGES/bar.po': pohelpers.makepo({
                        'label_login': ('Login', 'Connecter')})})

        spreadsheet = SpreadSheetMock()
        upload.upload(spreadsheet, self.tempdir, filter_translated=False,
                      languages=['de'],
                      output=None)
        self.assertEquals([{'package': u'foo',
                            'domain': u'bar',
                            'id': u'label_login',
                            'default': u'Login',
                            'translations': {u'de': u'Anmelden'},
                            }],
                          spreadsheet.uploaded)

    def test_filters_translated_languages_by_default(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/bar/locales/bar.pot': fshelpers.asset('empty.pot'),
                'foo/bar/locales/de/LC_MESSAGES/bar.po': pohelpers.makepo({
                        'label_login': ('Login', 'Anmelden'),
                        'label_logout': ('Logout', 'Abmelden')}),
                'foo/bar/locales/fr/LC_MESSAGES/bar.po': pohelpers.makepo({
                        'label_login': ('Login', 'Connecter'),
                        'label_logout': ('Logout', '')})})

        spreadsheet = SpreadSheetMock()
        upload.upload(spreadsheet, self.tempdir, filter_translated=True,
                      output=None)
        self.assertEquals([{'package': u'foo',
                            'domain': u'bar',
                            'id': u'label_logout',
                            'default': u'Logout',
                            'translations': {u'de': u'Abmelden',
                                             u'fr': u''},
                            }],
                          spreadsheet.uploaded)

    def test_uploading_additional_languages(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/bar/locales/bar.pot': fshelpers.asset('empty.pot'),
                'foo/bar/locales/de/LC_MESSAGES/bar.po': pohelpers.makepo({
                        'label_login': ('Login', 'Anmelden')}),
                'foo/bar/locales/fr/LC_MESSAGES/bar.po': pohelpers.makepo({
                        'label_login': ('Login', 'Connecter')})})

        spreadsheet = SpreadSheetMock()
        upload.upload(spreadsheet, self.tempdir, filter_translated=False,
                      languages=['de'], additional_languages=['fr'],
                      output=None)
        self.assertEquals([{'package': u'foo',
                            'domain': u'bar',
                            'id': u'label_login',
                            'default': u'Login',
                            'translations': {u'de': u'Anmelden',
                                             u'fr': u'Connecter'},
                            }],
                          spreadsheet.uploaded)

    def test_additional_languages_are_not_filtered_when_untranslated(self):
        fshelpers.create_structure(self.tempdir, {
                'foo/bar/locales/bar.pot': fshelpers.asset('empty.pot'),
                'foo/bar/locales/de/LC_MESSAGES/bar.po': pohelpers.makepo({
                        'label_login': ('Login', 'Anmelden')}),
                'foo/bar/locales/fr/LC_MESSAGES/bar.po': pohelpers.makepo({
                        'label_login': ('Login', 'Connecter')})})

        spreadsheet = SpreadSheetMock()
        upload.upload(spreadsheet, self.tempdir, filter_translated=True,
                      languages=['de'], additional_languages=['fr'],
                      output=None)
        self.assertEquals([],
                          spreadsheet.uploaded)
