from pprint import pprint
import sys

try:
    from ftw.recipe.translations import google
except ImportError, exc:
    print str(exc)
    print 'Run this script with ./bin/py test-google-auth.py'
    sys.exit(0)

TEST_DOC = 'https://docs.google.com/spreadsheet/ccc?key=0AgoYEZSDYCg1dEZvVGFTRUc3RDd6aFJsanA0VEx3Smc#gid=0'

spreadsheet = google.Spreadsheet()
spreadsheet.connect()
print 'Connection established'

spreadsheet.open(raw_input('Please enter the URL to a google document: ').strip()
                 or TEST_DOC)
print 'Document opened'
print 'Worksheets:', spreadsheet.worksheets()
print ''

upload_data = [{'package': 'ftw.book',
                'domain': 'plone',
                'id': 'Book',
                'default': 'Book',
                'translations': {'de': 'Buch',
                                 'en': 'Book'}},

               {'package': 'ftw.book',
                'domain': 'ftw.book',
                'id': 'book_label_layout',
                'default': 'Layout',
                'translations': {'de': 'Aussehen',
                                 'en': 'Layout'}}]

name = spreadsheet.upload(upload_data)
print 'Upload into new worksheet with name "%s"' % name
print '*' * 20
pprint(upload_data)
print '*' * 20
print ''

print 'Worksheets:', spreadsheet.worksheets()
print ''

print 'Export worksheet "%s"' % name
download_data = spreadsheet.download(name)
print '*' * 20
pprint(download_data)
print '*' * 20
print ''

assert download_data == upload_data, 'Uploaded and downloaded data does not match.'
print 'YAY, all OK'
