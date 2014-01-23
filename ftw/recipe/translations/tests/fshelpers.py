import os


def create_structure(basedir, structure):
    for path, data in structure.items():
        path = os.path.join(basedir, path)
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(path, 'w+') as file_:
            file_.write(data)
