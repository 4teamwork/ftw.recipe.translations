ftw.recipe.translations
=======================

``ftw.recipe.translations`` provides mass export / import of translations into / from
Google Docs spreadsheets for letting translators translate in a better environment.

Configuration
-------------

Using the buildout recipe generates a script ``bin/translations``:

.. code:: ini

    [buildout]
    parts = translations

    [translations]
    recipe = ftw.recipe.translations
    spreadsheet = https://docs.google.com/spreadsheet/ccc?key=0AgoYEZSDYCg1dEZvVGFTRUc3RDd6123DAFDER


The generated ``bin/translations`` script is preconfigured with the
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


The `sync` command
------------------

The ``bin/translations`` script provides a ``sync`` command for rebuilding
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

    ./bin/translations sync

Creating new languages for all packages and domains is as easy as passing
a positional argument:

.. code:: sh

    ./bin/translations sync de


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

    ./bin/translations upload de fr --additional-languages en es
    Spreadsheet: https://docs.google.com/spreadsheet/ccc?key=0AgoYEZ....
    Loading translations
    Starting Upload
    1 of 191 (0%): Upload
    9 of 191 (4%): Upload
    ...
    191 of 191 (100%): Upload


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

    ./bin/translated download
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


Links
-----

- github project: https://github.com/4teamwork/ftw.recipe.translations
- Issue tracker: https://github.com/4teamwork/ftw.recipe.translations/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.recipe.translations
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.recipe.translations


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.recipe.translations`` is licensed under GNU General Public License, version 2.
