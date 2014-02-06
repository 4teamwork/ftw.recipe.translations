from ftw.recipe.translations import discovery
from ftw.recipe.translations.discovery import discover_package
from ftw.recipe.translations.utils import chdir
from i18ndude.catalog import MessageCatalog
from i18ndude.catalog import POWriter
import i18ndude.script
import os.path


class Arguments(dict):
    def __init__(self, *args, **kwargs):
        super(Arguments, self).__init__(*args, **kwargs)
        self.__dict__ = self


def rebuild_package_potfiles(package_dir, primary_domain):
    for group in discover_package(package_dir, None):
        if group['domain'] != primary_domain:
            continue

        manual = ''
        if group['manual']:
            manual = os.path.join(package_dir, group['manual'])

        potpath = os.path.join(package_dir, group['pot'])
        rebuild_pot(package_dir, primary_domain, potpath, manual)


def rebuild_pot(package_dir, domain, potpath, manual):
    arguments = Arguments({'pot_fn': potpath,
                           'create_domain': domain,
                           'path': ['.'],
                           'exclude': '',
                           'merge_fn': manual,
                           'merge2_fn': ''})

    with chdir(package_dir):
        i18ndude.script.rebuild_pot(arguments)


def sync_pofiles(sources_directory, languages):
    for group in discovery.discover(sources_directory):
        if not group['pot']:
            continue

        sync_pofile_group(sources_directory, group, languages)


def sync_pofile_group(sources_directory, group, languages):
    pofiles = []
    for lang, popath in group['languages'].items():
        if languages is not None and lang not in languages:
            continue
        pofiles.append(os.path.join(sources_directory,
                                    group['package'],
                                    popath))

    for lang in set(languages or []) - set(group['languages'].keys()):
        path = os.path.join(sources_directory,
                            group['package'],
                            group['locales'],
                            lang,
                            'LC_MESSAGES',
                            '%s.po' % group['domain'])
        create_new_pofile(path, group['domain'])
        pofiles.append(path)

    potpath = os.path.join(sources_directory,
                           group['package'],
                           group['pot'])


    arguments = Arguments({'pot_fn': potpath,
                           'files': pofiles})
    i18ndude.script.sync(arguments)

def create_new_pofile(path, domain):
    catalog = MessageCatalog(domain=domain)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'w+') as file_:
        POWriter(file_, catalog).write(msgstrToComment=False,
                                       sync=True)