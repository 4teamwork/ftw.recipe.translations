from i18ndude.catalog import MessageCatalog
from i18ndude.catalog import POWriter
from json import load
import os
import re


def rebuild_pot(potfile, package_dir, i18n_domain):
    if not os.path.exists(package_dir):
        return

    translatable_key_expr = re.compile(
        r'^[^:]*:translate\(%s\)$' % re.escape(i18n_domain))

    content_creation_files = []
    for dirpath, dirnames, filenames in os.walk(package_dir):
        if not dirpath.rstrip('/').endswith('/content_creation'):
            continue

        content_creation_files.extend(
            [os.path.join(dirpath, name) for name in [name for name in filenames if name.endswith('.json')]])

    msgids = set()
    for jsonpath in content_creation_files:
        data = load(open(jsonpath))
        msgids.update(get_translated_values(data, translatable_key_expr))

    if not msgids:
        return

    catalog = MessageCatalog(domain=i18n_domain)
    for msgid in msgids:
        catalog.add(msgid)

    potfile_dir = os.path.dirname(potfile)
    if not os.path.exists(potfile_dir):
        os.makedirs(potfile_dir)

    with open(potfile, 'w') as potfile:
        writer = POWriter(potfile, catalog)
        writer.write(msgstrToComment=True)


def get_translated_values(data, translatable_key_expr):
    if isinstance(data, dict):
        for key, value in data.items():
            if translatable_key_expr.match(key):
                yield value
            for result in get_translated_values(value, translatable_key_expr):
                yield result

    elif isinstance(data, list) or isinstance(data, tuple) or isinstance(data, set):
        for value in data:
            for result in get_translated_values(value, translatable_key_expr):
                yield result
