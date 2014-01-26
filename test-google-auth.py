import sys

try:
    from ftw.recipe.translations import google
except ImportError, exc:
    print str(exc)
    print 'Run this script with ./bin/py test-google-auth.py'
    sys.exit(0)

print google.Connector()()
