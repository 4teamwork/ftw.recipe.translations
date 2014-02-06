from zc.recipe.egg import Egg


class Recipe(Egg):

    def __init__(self, buildout, name, options):
        assert options.get('package-name'), '%s:package-name is required' % name
        name = 'ftw.recipe.translations'

        # Only install "bin/i18n-build" script, not other scripts.
        options['scripts'] = 'i18n-build'

        kwargs = {'package_name': options.get('package-name'),
                  'i18n_domain': options.get('i18n-domain'),
                  'package_namespace': options.get('package-namespace'),
                  'package_directory': options.get('package-directory')}
        options['arguments'] = ', '.join(
            ['%s="%s"' % (key, value) for (key, value) in kwargs.items()])

        super(Recipe, self).__init__(buildout, name, options)
