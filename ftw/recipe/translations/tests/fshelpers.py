from path import Path
from six.moves import map
import os


def create_structure(*dirs_and_structure):
    structure = dirs_and_structure[-1]
    if len(dirs_and_structure) > 1:
        basedir = resolve_to_path(dirs_and_structure[:-1])
    else:
        basedir = None

    for filepath, data in structure.items():
        filepath = resolve_to_path((basedir, filepath))
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(filepath, 'w+') as file_:
            file_.write(data)


def cat(*pathparts):
    filepath = resolve_to_path(pathparts)
    with open(filepath) as file_:
        return file_.read()


def asset(name):
    """Returns the content of a testing asset.
    """
    filepath = os.path.join(os.path.dirname(__file__), 'assets', name)
    with open(filepath) as file_:
        return file_.read()


def files(directory):
    for filepath in Path(directory).walkfiles():
        yield str(filepath.relpath(directory))


def resolve_to_path(pathparts):
    if isinstance(pathparts, (list, tuple)):
        return os.path.join(*list(map(resolve_to_path, pathparts)))
    elif isinstance(pathparts, str):
        return pathparts.encode('utf-8')
    else:
        return pathparts
