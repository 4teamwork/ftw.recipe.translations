from ftw.recipe.translations.discovery import discover
from i18ndude.catalog import MessageCatalog
from i18ndude.catalog import POWriter
import os.path


def write_catalog(sources_directory, catalog):
    registry = PofileRegistry(sources_directory)

    for message in catalog.messages:
        for language, msgstr in message.translations.items():
            pofile = registry.find_pofile_for(message, language)
            target_message = pofile.get(message.msgid)
            if target_message is None:
                print(('Warning: Ignoring "{0}" of "{1}" because it does no'
                       ' longer exist.'.format(message.msgid, message.domain)))
                continue
            target_message.msgstr = msgstr

    registry.write_pofiles()


def cleanup_pofile(path):
    with open(path, 'r') as file_:
        lines = file_.read().split('\n')

    with open(path, 'w') as file_:
        for line in lines:
            if line.startswith('"Language-Code:') or \
                    line.startswith('"Language-Name:'):
                continue

            if line.startswith('"Domain:'):
                continue

            file_.write(line + '\n')


class PofileRegistry(object):

    def __init__(self, sources_directory):
        self.sources_directory = sources_directory
        self.catalogs = {}
        self.domains = self._discover_domains()

    def find_pofile_for(self, message, language):
        key = (message.package, message.domain, language)
        if key not in self.catalogs:
            path = self.find_pofile_path_for(message, language)
            self.catalogs[key] = MessageCatalog(path)

        return self.catalogs[key]

    def find_pofile_path_for(self, message, language):
        domain = self.domains[message.package, message.domain]
        relative_path = domain['languages'][language]
        return os.path.join(self.sources_directory,
                            domain['package'],
                            relative_path)

    def write_pofiles(self):
        for catalog in self.catalogs.values():
            with open(catalog.filename, 'w+') as file_:
                POWriter(file_, catalog).write(msgstrToComment=False,
                                               sync=True)
            cleanup_pofile(catalog.filename)

    def _discover_domains(self):
        result = {}
        for group in discover(self.sources_directory):
            key = (group['package'], group['domain'])
            result[key] = group
        return result
