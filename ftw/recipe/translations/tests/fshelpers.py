from path import path
import os


def create_structure(basedir, structure):
    for filepath, data in structure.items():
        filepath = os.path.join(basedir, filepath)
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(filepath, 'w+') as file_:
            file_.write(data)


def cat(basedir, relpath):
    filepath = os.path.join(basedir, relpath)
    with open(filepath) as file_:
        return file_.read()


def asset(name):
    """Returns the content of a testing asset.
    """
    filepath = os.path.join(os.path.dirname(__file__), 'assets', name)
    with open(filepath) as file_:
        return file_.read()


def files(directory):
    for filepath in path(directory).walkfiles():
        yield str(filepath.relpath(directory))
