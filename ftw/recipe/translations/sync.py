from StringIO import StringIO
from ftw.recipe.translations import discovery
from ftw.recipe.translations.utils import capture_streams
from ftw.recipe.translations.utils import chdir
from i18ndude.catalog import MessageCatalog
from i18ndude.catalog import POWriter
import i18ndude.script
import os.path
import sys


def setup_argparser(subparsers):
    subparser = subparsers.add_parser('sync', help=synchronize.__doc__)
    subparser.set_defaults(func=synchronize_command)

    subparser.add_argument(
        'languages', nargs='*', metavar='lang',
        help='Language code of languages to synchronize.' + \
            ' If defined, only the defined languages are synchronized' + \
            ' and will be created if missing.')

def synchronize_command(args):
    return synchronize(args.sources_dir, args.languages)


def synchronize(sources_directory, languages=None, output=sys.stdout):
    """Rebuilds .pot-files of the default domain of each package in the
    source directory and syncs all .po-files with the .pot-files of all
    domains in each package.
    """
    with capture_streams(stdout=output or StringIO()):
        rebuild_primary_domain_group_potfiles(sources_directory)
        sync_pofiles(sources_directory, languages)


class Arguments(dict):
    def __init__(self, *args, **kwargs):
        super(Arguments, self).__init__(*args, **kwargs)
        self.__dict__ = self


def rebuild_primary_domain_group_potfiles(sources_directory):
    for group in discovery.discover(sources_directory):
        if not group['pot']:
            continue

        if group['package'] != group['domain']:
            continue

        locales = os.path.join(sources_directory, group['package'],
                               group['locales'])
        package_dir = os.path.join(sources_directory, group['package'])
        sourcedir = './' + os.path.relpath(
            os.path.abspath(os.path.join(locales, '..')),
            package_dir)
        potpath = os.path.join(package_dir, group['pot'])

        manual = ''
        if group['manual']:
            manual = os.path.join(package_dir, group['manual'])

        rebuild_pot(package_dir, sourcedir, group['domain'], potpath, manual)


def rebuild_pot(package_dir, sourcedir, domain, potpath, manual):
    arguments = Arguments({'pot_fn': potpath,
                           'create_domain': domain,
                           'path': [sourcedir],
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
