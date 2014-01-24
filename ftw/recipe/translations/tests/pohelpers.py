from i18ndude.catalog import MessageCatalog
import os.path


def messages(*pathparts):
    """Returns a dict of messages (msgid => msgstr) of the po file of which
    the path is passed as argument list.
    """
    path = os.path.join(*pathparts).encode('utf-8')
    catalog = MessageCatalog(path)

    messages = {}
    for msg in catalog.values():
        messages[msg.msgid] = msg.msgstr
    return messages
