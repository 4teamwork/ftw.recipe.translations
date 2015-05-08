=========================
 ftw.recipe.translations
=========================

``ftw.recipe.translations`` provides mass theese features:

- ``bin/i18n-build``: Package rebuilding script for installing in a single package.

- ``bin/masstranslate``: export / import of translations into / from Google
  Docs spreadsheets for letting translators translate in a better environment.

.. contents:: Table of Contents


bin/i18n-build
==============

The ``i18n-build`` script is installed for a single package.
When executed, all languages of all domains translated in this package are rebuilt.

The script expectes exactly one primary domain.
The domain name is expected to be equal to the package name (configurable).

What the script does:

- The script rebuilds the primary package using `i18ndude`: it scans for translated
  strings in the code and rebuilds the `.pot` of the primary domain.

- It syncs the `.po`-files of all domains in all languages.


Installation and configuration
------------------------------

For installation simply use the zc.buildout recipe ``ftw.recipe.translations:package``:

.. code:: ini

    [buildout]
    parts = i18n-build

    [i18n-build]
    recipe = ftw.recipe.translations:package
    package-name = my.package

**Problems with ``six``**:

``ftw.recipe.translations`` requires the ``oauth2client`` package, which requires
``six``.
Since Plone 4.3 requires an older ``six`` version
(``1.2.0``, but ``1.4.0`` would work too) we use an older,
compatible ``oauth2client`` version.
If you install ``ftw.recipe.translations`` with Plone 4.2 or older, there is no
version pinning and you need to pin down ``six``.
We propose to use ``six = 1.4.0``, which is also compatible with ``lovely.buildouthttp``:

.. code:: ini

    [versions]
    six = 1.4.0

**Options:**

package-name
  The setuptools-name of the package (required).

i18n-domain
  The name of the primary domain of this package (optional, defaults to the package name).

package-namespace
  The package namespace used for scanning the code when rebuilding the
  primary domain (optional, defaults to the the package name).

**Full example:**

.. code:: ini

    [buildout]
    parts = i18n-build

    [i18n-build]
    recipe = ftw.recipe.translations:package
    package-name = MyPackage
    i18n-domain = mypackage
    package-namespace = my.package


Usage
-----

Rebuilding and syncing all existing languages:

.. code:: sh

    $ bin/i18n-build
    Rebuilding .../my/package/locales/mypackage.pot
    .../my/package/locales/de/LC_MESSAGES/mypackage.po: 0 added, 2 removed
    .../my/package/locales/en/LC_MESSAGES/mypackage.po: 1 added, 2 removed
    .../my/package/locales/de/LC_MESSAGES/plone.po: 1 added
    .../my/package/locales/en/LC_MESSAGES/plone.po: 1 added


Creating translations (.po-files) for new languages:

.. code:: sh

    $ bin/i18n-build fr it
    Rebuilding .../my/package/locales/mypackage.pot
    .../my/package/locales/de/LC_MESSAGES/mypackage.po: 0 added, 2 removed
    .../my/package/locales/en/LC_MESSAGES/mypackage.po: 1 added, 2 removed
    .../my/package/locales/fr/LC_MESSAGES/mypackage.po: 80 added, 0 removed
    .../my/package/locales/it/LC_MESSAGES/mypackage.po: 80 added, 0 removed
    .../my/package/locales/de/LC_MESSAGES/plone.po: 1 added
    .../my/package/locales/en/LC_MESSAGES/plone.po: 1 added
    .../my/package/locales/fr/LC_MESSAGES/plone.po: 3 added, 0 removed
    .../my/package/locales/it/LC_MESSAGES/plone.po: 3 added, 0 removed




bin/masstranslate
=================

The ``masstranslate`` script is installed in a buildout which checks out
all relevant packages into an ``src``-directory (e.g. using ``mr.developer``).

You then can upload all translations of all packages in the source-directory
into a Googlea spreadsheet for translation.
When the translation is done in the Google spreadsheet the script can download
all translations and sync them back to the right place in the packages.

Installation and Configuration
------------------------------

Using the buildout recipe generates a script ``bin/masstranslate``:

.. code:: ini

    [buildout]
    parts = translations

    [translations]
    recipe = ftw.recipe.translations
    spreadsheet = https://docs.google.com/spreadsheet/ccc?key=0AgoYEZSDYCg1dEZvVGFTRUc3RDd6123DAFDER


The generated ``bin/masstranslate`` script is preconfigured with the
configured ``spreadsheet`` url and applies to all .po-files in the
``./src`` directory by default.


Google authentication and authorization
---------------------------------------

Google auth is implemented using OAuth2.
This means you require to have an application set up in your
Google API Console or at least have the application secrets (.json) of such
an application.
The application secrets need to be copied to
``~/.buildout/ftw.recipe.translations.json``.
For instructions for creating a Google application see the
`Wiki page <https://github.com/4teamwork/ftw.recipe.translations/wiki/Creating%20a%20Google%20OAuth%20Application>`_.

When using the ``upload`` and ``download`` commands, the OAuth2 authentication
is done with the configure application.
The browser is opened and the user can grant access for the application
to his Google Drive.
The received ticket is stored in the users keyring / keychain.

If the server in your running this script do not have a web browser (for instance
you are running it in a shared computer logged-in through SSH), the browser
that pops-up is unable to handle the authorization process or if you prefer
to authorize the application using your own web browser; add the
``--noauth_local_webserver=True`` parameter to the script. Using this option the
script will show a URL which you should open with your browser manualy, and later
enter the authorization code showed in that browser back in the console.


The `sync` command
------------------

The ``bin/masstranslate`` script provides a ``sync`` command for rebuilding
primary-domain .pot-files and syncing them with all languages.

As **primary domain** the package name (folder in the ``src`` directory) is
expected.
Primary domains are rebuilt (the package is searched for translatable
strings) and ``[domain]-manual.pot``-files in the ``locales``
directory are automatically merged.
Non-primary domains are never rebuilt and expected to be updated manually.

All domains are then sync to all existing languages.

Example:

.. code:: sh

    ./bin/masstranslate sync

Creating new languages for all packages and domains is as easy as passing
a positional argument:

.. code:: sh

    ./bin/masstranslate sync de


The `upload` command
--------------------

With the upload command translations can easily be extracted from the
``.po``-Files and uploaded into a Google spreadsheet.
The ``upload`` command always creates a new worksheet in the Google spreadsheet,
so that existing data is never overwritten.

See the ``Configuration`` section on how to configure the spreadsheet URL.

With positional arguments the languages to be translated can be specificied.
Each defined language is included in the spreadsheet.
If a message is translated in all languages, the message is not uploaded
unless the ``--all`` keyword is used.

Additional languages, which are not checked for existing translations, can
be added using the ``--additional-languages`` keyword, those may be useful
for the translator.

Example:

.. code:: sh

    ./bin/masstranslate upload de fr --additional-languages en es
    Spreadsheet: https://docs.google.com/spreadsheet/ccc?key=0AgoYEZ....
    Loading translations
    Starting Upload
    1 of 191 (0%): Upload
    9 of 191 (4%): Upload
    ...
    Finished Upload
    Uploaded into worksheet "013: 2014-01-31"

The `download` command
----------------------

The download command syncs translations back from the spreadsheet into the
``.po``-files in the source directory.
When starting a download, the user is asked for the worksheet and languages
to download.
When a message is not translated in the spreadsheet, it is never updated
in the .po-file.

Example:

.. code:: sh

    ./bin/masstranslate download
    Please select a worksheet to download:
    [1] 011: 2014-01-31
    [2] 012: 2014-01-31
    [3] 013: 2014-01-31

    Please enter the spreadsheet number: 1
    Please select the languages to synchronize:
    - de
    - fr

    Enter one language code at a time, finish selection with an empty enter.
    Language: fr
    Language:


Translation headers
===================

The syncing commands remove the .po-file header `Domain`, `Language-Name` and
`Language-Code`. The reason for this behavior is that this package is primarely
made for Plone packages and Plone does not read those headers (it gets the
information from the paths, e.g. `locales/[lang-code]/LC_MESSAGES/[domain].po`).
Because the headers are not relevant they are often not maintained properly and
therefore usually wrong.


Links
=====

- github project: https://github.com/4teamwork/ftw.recipe.translations
- Issues: https://github.com/4teamwork/ftw.recipe.translations/issues
- Pypi: http://pypi.python.org/pypi/ftw.recipe.translations
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.recipe.translations


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.recipe.translations`` is licensed under GNU General Public License, version 2.
