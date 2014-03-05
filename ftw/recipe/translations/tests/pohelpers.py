from StringIO import StringIO
from ftw.recipe.translations.tests import fshelpers
from i18ndude.catalog import MessageCatalog
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
    headers = filter(re.compile('".*:.*"').match, lines)
    headers = map(lambda line: line.rstrip('"').lstrip('"'), headers)
    headers = map(lambda line: map(str.strip, line.split(':', 1)), headers)
    return dict(headers)


def makepo(messages):
    data = StringIO()
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
