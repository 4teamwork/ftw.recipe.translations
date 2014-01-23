
class Catalog(object):

    def __init__(self):
        self.catalog = {}

    def get_message(self, package, domain, msgid, default=None):
        """Returns a message object, creates it when necessary.
        """

        key = (package, domain, msgid)
        if key in self.catalog:
            return self.catalog[key]

        message = Message(package, domain, msgid, default)
        self.add_message(message)
        return message

    def add_message(self, message):
        key = (message.package, message.domain, message.msgid)
        if key in self.catalog:
            raise ValueError('Message %s already registered' % key)

        self.catalog[key] = message

    @property
    def messages(self):
        return self.catalog.values()


class Message(object):

    def __init__(self, package, domain, msgid, default):
        self.package = package
        self.domain = domain
        self.msgid = msgid
        self.default = default
        self.translations = {}

    def translate(self, language, msgstr):
        self.translations[language] = msgstr
