from StringIO import StringIO
from ftw.recipe.translations import utils
from unittest2 import TestCase
import os
import sys
import tempfile


class TestCaptureStreams(TestCase):

    def test_captures_stdout(self):
        stdout = StringIO()
        with utils.capture_streams(stdout=stdout):
            print 'Foo'
        self.assertEquals('Foo\n', stdout.getvalue())

    def test_captures_stderr(self):
        stderr = StringIO()
        with utils.capture_streams(stderr=stderr):
            print >> sys.stderr, 'Error'
        self.assertEquals('Error\n', stderr.getvalue())

    def test_captures_all_streams_parallel(self):
        stdout = StringIO()
        stderr = StringIO()
        with utils.capture_streams(stdout=stdout, stderr=stderr):
            print 'Foo'
            print >> sys.stderr, 'Bar'
        self.assertEquals('Foo\n', stdout.getvalue())
        self.assertEquals('Bar\n', stderr.getvalue())
