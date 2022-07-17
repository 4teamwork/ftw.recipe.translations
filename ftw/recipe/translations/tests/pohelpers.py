from ftw.recipe.translations.tests import fshelpers
from i18ndude.catalog import MessageCatalog
from io import BytesIO
from six.moves import filter
from six.moves import map
import re


def messages(*pathparts):
    """Returns a dict of messages (msgid => msgstr) of the po file of which
    the path is passed as argument list.
    """
    path = fshelpers.resolve_to_path(pathparts)
    catalog = MessageCatalog(path)

    messages = {}
    for msg in catalog.values():
        messages[msg.msgid] = msg.msgstr
    return messages


def message_references(*pathparts):
    path = fshelpers.resolve_to_path(pathparts)
    catalog = MessageCatalog(path)

    messages = {}
    for msg in catalog.values():
        messages[msg.msgid] = msg.references
    return messages


def headers(*pathparts):
    lines = fshelpers.cat(pathparts).split('\n')
    headers = list(filter(re.compile('".*:.*"').match, lines))
    headers = [line.rstrip('"').lstrip('"') for line in headers]
    headers = [list(map(str.strip, line.split(':', 1))) for line in headers]
    return dict(headers)


def makepo(messages):
    data = BytesIO()
    data.write(fshelpers.asset('empty.po'))

    for msgid, value in sorted(messages.items()):
        if isinstance(value, tuple):
            default, msgstr = value
        else:
            default, msgstr = None, value

        data.write('\n\n')
        if default:
            data.write('#. Default: "%s"\n' % default)
        data.write('msgid "%s"\n' % msgid)
        data.write('msgstr "%s"\n' % msgstr)

    return data.getvalue().strip()
