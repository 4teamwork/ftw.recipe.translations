import os
from setuptools import setup, find_packages


version = '1.2.5.dev0'


tests_require = [
    'mocker',
    'plone.testing',
    'unittest2',
]


setup(name='ftw.recipe.translations',
      version=version,
      description='Mass export / import of translations into' + \
      ' Google Docs Spreadsheets',

      long_description=open('README.rst').read() + '\n' + \
      open(os.path.join('docs', 'HISTORY.txt')).read(),

      classifiers=[
          'Framework :: Plone',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],

      keywords='ftw recipe translations import export google docs',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.recipe.translations',

      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw', 'ftw.recipe'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'argparse',
          'gspread',
          'i18ndude',
          'keyring',
          'path.py',
          'setuptools',
          'zc.buildout',
          'zc.recipe.egg',

        # oauth2client 1.4.12 is the first version with acceptable dependency
          # declaration. So we take at least this one. NOTE: This may breake
          # compatibility with Plone 4.3.2 and older.
        'oauth2client <= 1.4.12',
      ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      entry_points = {
          'zc.buildout': [
              'default = ftw.recipe.translations.masstranslate.recipe:Recipe',
              'package = ftw.recipe.translations.i18nbuild.recipe:Recipe'],
          'console_scripts': [
              'masstranslate = ftw.recipe.translations.masstranslate.command:main',
              'i18n-build = ftw.recipe.translations.i18nbuild.command:main']
      },
)
