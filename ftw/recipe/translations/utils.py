from contextlib import contextmanager
from pkg_resources import get_distribution
import os
import sys


def find_package_directory(buildout_dir, package_name, package_namespace):
    namepath = package_name.replace('.', '/')
    for each in (namepath,
                 package_namespace,
                 os.path.join('src', namepath),
                 os.path.join('src', package_name, namepath)):
        if each is None:
            continue

        directory = os.path.join(buildout_dir, each)
        if os.path.exists(directory) and os.path.isdir(directory):
            return directory


def version():
    return get_distribution('ftw.recipe.translations').version


@contextmanager
def capture_streams(stdout=None, stderr=None):
    ori_stdout = sys.stdout
    ori_stderr = sys.stderr

    if stdout is not None:
        sys.stdout = stdout
    if stderr is not None:
        sys.stderr = stderr

    try:
        yield
    finally:
        if stdout is not None:
            sys.stdout = ori_stdout
        if stderr is not None:
            sys.stderr = ori_stderr


@contextmanager
def chdir(path):
    before = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(before)
