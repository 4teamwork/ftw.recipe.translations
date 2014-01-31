from collections import defaultdict
from path import path
import os.path
import re


def discover(sources_directory):
    Group = lambda: {u'package': None,
                     u'domain': None,
                     u'locales': None,
                     u'pot': None,
                     u'manual': None,
                     u'languages': {}}
    items = defaultdict(Group)

    for match in _find_po_files(sources_directory):
        group = items[match[u'package'], match[u'domain']]
        group[u'languages'][match[u'language']] = unicode(
            match[u'relative_path'])

        if group['locales'] is None:
            group['locales'] = match['locales']
        if group['locales'] != match['locales']:
            raise ValueError((
                    'Unexpected locales directory %s for file %s; '
                    'expected locales directory to be %s') % (
                    match['locales'], match['absolute_path'],
                    match['locales']))

    for match in _find_pot_files(sources_directory):
        group = items[match[u'package'], match[u'domain']]
        group[u'pot'] = unicode(match[u'relative_path'])
        group[u'manual'] = match[u'manual']

        if group['locales'] is None:
            group['locales'] = match['locales']
        if group['locales'] != match['locales']:
            raise ValueError((
                    'Unexpected locales directory %s for file %s; '
                    'expected locales directory to be %s') % (
                    match['locales'], match['absolute_path'],
                    match['locales']))

    for key, value in items.items():
        package, domain = key
        value[u'package'] = package
        value[u'domain'] = domain

    return items.values()


def _find_po_files(sources_directory):
    for filepath in path(sources_directory).walkfiles(u'*.po'):
        if not re.match('.*locales/[^/]*/LC_MESSAGES/[^/]*\.po$', filepath):
            continue
        src_rel_path = filepath.relpath(sources_directory)
        pkg_rel_path = '/'.join(src_rel_path.split('/')[1:])
        locales_path = '/'.join(pkg_rel_path.split('/')[:-3])
        yield {u'package': src_rel_path.split(u'/')[0],
               u'domain': unicode(src_rel_path.basename().splitext()[0]),
               u'locales': locales_path,
               u'language': src_rel_path.split(u'/')[-3],
               u'relative_path': pkg_rel_path,
               u'absolute_path': filepath}


def _find_pot_files(sources_directory):
    for filepath in path(sources_directory).walkfiles(u'*.pot'):
        if not re.match('.*locales/.*\.pot$', filepath):
            continue
        if re.match('/.*-manual\.pot$', filepath):
            continue

        package_name = filepath.relpath(sources_directory).split('/')[0]
        package_path = os.path.join(sources_directory, package_name)

        manual = None
        manual_path = re.sub('\.pot$', '-manual.pot', filepath)
        if os.path.exists(manual_path):
            manual = unicode(path(manual_path).relpath(package_path))

        yield {u'package': package_name,
               u'domain': unicode(filepath.basename().splitext()[0]),
               u'locales': os.path.dirname(path(filepath).relpath(package_path)),
               u'relative_path': path(filepath).relpath(package_path),
               u'absolute_path': filepath,
               u'manual': manual}
