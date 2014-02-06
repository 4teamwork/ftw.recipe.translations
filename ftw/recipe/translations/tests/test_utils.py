from StringIO import StringIO
from ftw.recipe.translations import utils
from unittest2 import TestCase
import os
import sys
import tempfile
from ftw.recipe.translations.testing import TEMP_DIRECTORY_FIXTURE
from ftw.recipe.translations.utils import find_package_directory


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


class TestFindPackageNamespace(TestCase):

    layer = TEMP_DIRECTORY_FIXTURE

    def setUp(self):
        self.tempdir = self.layer['tempdir']

    def test_find_package_directory(self):
        os.makedirs(os.path.join(self.tempdir, 'foo/bar'))

        directory = find_package_directory(self.tempdir, 'foo.bar')
        self.assertEqual(os.path.join(self.tempdir, 'foo/bar'), directory)

    def test_find_package_directory_in_src_folder(self):
        os.makedirs(os.path.join(self.tempdir, 'src/foo/bar'))

        directory = find_package_directory(self.tempdir, 'foo.bar')
        self.assertEqual(os.path.join(self.tempdir, 'src/foo/bar'), directory)

    def test_find_package_directory_in_src_namespace_folder(self):
        os.makedirs(os.path.join(self.tempdir, 'src/foo.bar/foo/bar'))

        directory = find_package_directory(self.tempdir, 'foo.bar')
        self.assertEqual(os.path.join(self.tempdir, 'src/foo.bar/foo/bar'),
                         directory)

