from zc.recipe.egg import Egg
import os.path


class Recipe(Egg):

    def __init__(self, buildout, name, options):
        self.options = options

        # rename script to part name
        options['scripts'] = 'translations=%s' % name

        # initialize sources_dir variable, based on mr.developer config
        sources_dir = buildout['buildout'].get('sources-dir')
        if not sources_dir:
            sources_dir = os.path.join(
                buildout['buildout'].get('directory'), 'src')
        self._extend_initialization('sources_dir = "%s"' % sources_dir)
        self._add_script_argument('sources_dir')

        # initialize spreadsheet variable
        spreadsheet = options.get('spreadsheet', None)
        if spreadsheet:
            self._extend_initialization('spreadsheet = "%s"' % spreadsheet)
        else:
            self._extend_initialization('spreadsheet = None')
        self._add_script_argument('spreadsheet')

        super(Recipe, self).__init__(buildout, name, options)
        self.default_eggs = 'ftw.recipe.translations'

    def _extend_initialization(self, code):
        self.options['initialization'] = '\n'.join((
                self.options.get('initialization', ''),
                code))

    def _add_script_argument(self, argument):
        arguments = self.options.get('arguments')
        if arguments:
            self.options['arguments'] = '%s, %s' % (argument, arguments)
        else:
            self.options['arguments'] = argument
