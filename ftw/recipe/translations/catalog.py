
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

    def get_message_dicts(self, languages=None):
        return [msg.to_dict(languages) for msg in self.messages]


class Message(object):

    def __init__(self, package, domain, msgid, default):
        self.package = package
        self.domain = domain
        self.msgid = msgid
        self.default = default
        self.translations = {}

    def translate(self, language, msgstr):
        self.translations[language] = msgstr

    def to_dict(self, languages=None):
        data = {'package': self.package,
                'domain': self.domain,
                'id': self.msgid,
                'default': self.default,
                'translations': {}}

        if languages:
            for lang in languages:
                data['translations'][lang] = self.translations.get(lang, '')
        else:
            data['translations'] = self.translations.copy()

        return data
