from ftw.recipe.translations.catalog import Catalog
from ftw.recipe.translations.discovery import discover
from i18ndude.catalog import MessageCatalog
import os.path


def load_translation_catalog(sources_directory):
    catalog = Catalog()

    for group in discover(sources_directory):
        update_catalog_with_language_translations(sources_directory,
                                                  catalog,
                                                  group)

    return catalog


def update_catalog_with_language_translations(sources_directory,
                                              catalog,
                                              group):

    for language, relpath in group['languages'].items():
        pofile = os.path.join(sources_directory, group['package'], relpath)

        for msgid, msgstr, default in get_translations_from_file(pofile):
            message = catalog.get_message(package=group['package'],
                                          domain=group['domain'],
                                          msgid=msgid,
                                          default=default)
            message.translate(language, msgstr)


def get_translations_from_file(pofile):
    file_catalog = MessageCatalog(pofile)
    for message in file_catalog.values():
        default = message.getDefault()
        if default:
            default = default.decode('utf-8')

        yield message.msgid, message.msgstr, default
