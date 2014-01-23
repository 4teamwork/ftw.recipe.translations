import os


def create_structure(basedir, structure):
    for path, data in structure.items():
        path = os.path.join(basedir, path)
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(path, 'w+') as file_:
            file_.write(data)


def asset(name):
    """Returns the content of a testing asset.
    """
    path = os.path.join(os.path.dirname(__file__), 'assets', name)
    with open(path) as file_:
        return file_.read()
