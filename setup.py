import os
from setuptools import setup, find_packages


version = '1.0.1'


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
        'oauth2client',
        'path.py',
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        ],

      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      entry_points = {
        'zc.buildout': [
            'default = ftw.recipe.translations.recipe:Recipe'],
        'console_scripts': [
            'translations = ftw.recipe.translations.command:main']
        },
      )
