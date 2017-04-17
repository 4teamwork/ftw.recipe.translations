from collections import defaultdict
from path import Path
import os.path
import re


def discover_package(package_dir, package_name=None):
    Group = lambda: {u'package': None,
                     u'domain': None,
                     u'locales': None,
                     u'pot': None,
                     u'manual': None,
                     u'content': None,
                     u'lawgiver': None,
                     u'languages': {}}
    items = defaultdict(Group)

    for match in _find_po_files(package_dir, package_name):
        group = items[(match[u'locales'], match['domain'], match['package'])]
        group[u'languages'][match[u'language']] = unicode(
            match[u'relative_path'])

        group[u'locales'] = match[u'locales']
        group[u'domain'] = match['domain']
        group[u'package'] = match['package']

    for match in _find_pot_files(package_dir, package_name):
        group = items[(match[u'locales'], match['domain'], match['package'])]
        group[u'pot'] = unicode(match[u'relative_path'])
        group[u'manual'] = match[u'manual']
        group[u'content'] = match[u'content']
        group[u'lawgiver'] = match[u'lawgiver']

        group[u'locales'] = match[u'locales']
        group[u'domain'] = match['domain']
        group[u'package'] = match['package']

    return items.values()


def discover(sources_directory):
    result = []
    for package_name in os.listdir(sources_directory):
        package_dir = os.path.join(sources_directory, package_name)
        if os.path.isdir(package_dir):
            result.extend(discover_package(package_dir, package_name))
    return result


def _find_po_files(package_dir, package_name):
    for filepath in Path(package_dir).walkfiles(u'*.po'):
        if not re.match('.*locales/[^/]*/LC_MESSAGES/[^/]*\.po$', filepath):
            continue
        rel_path = filepath.relpath(package_dir)
        locales_path = '/'.join(rel_path.split('/')[:-3])
        yield {u'package': package_name,
               u'domain': unicode(rel_path.basename().splitext()[0]),
               u'locales': locales_path,
               u'language': rel_path.split(u'/')[-3],
               u'relative_path': rel_path,
               u'absolute_path': filepath}


def _find_pot_files(package_dir, package_name):
    for filepath in Path(package_dir).walkfiles(u'*.pot'):
        if not re.match('.*locales/.*\.pot$', filepath):
            continue
        if re.match('/.*-manual\.pot$', filepath):
            continue
        if re.match('/.*-content\.pot$', filepath):
            continue
        if re.match('/.*-lawgiver\.pot$', filepath):
            continue

        manual = None
        manual_path = re.sub('\.pot$', '-manual.pot', filepath)
        if os.path.exists(manual_path):
            manual = unicode(Path(manual_path).relpath(package_dir))

        content = None
        content_path = re.sub('\.pot$', '-content.pot', filepath)
        if os.path.exists(content_path):
            content = unicode(Path(content_path).relpath(package_dir))

        lawgiver = None
        lawgiver_path = re.sub('\.pot$', '-lawgiver.pot', filepath)
        if os.path.exists(lawgiver_path):
            lawgiver = unicode(path(lawgiver_path).relpath(package_dir))

        yield {u'package': package_name,
               u'domain': unicode(filepath.basename().splitext()[0]),
               u'locales': os.path.dirname(Path(filepath)
                                           .relpath(package_dir)),
               u'relative_path': Path(filepath).relpath(package_dir),
               u'absolute_path': filepath,
               u'manual': manual,
               u'content': content,
               u'lawgiver': lawgiver}
