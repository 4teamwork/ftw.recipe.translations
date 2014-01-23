from zc.recipe.egg import Egg


class Recipe(Egg):

    def __init__(self, buildout, name, options):
        options['scripts'] = 'translations=%s' % name
        super(Recipe, self).__init__(buildout, name, options)
        self.default_eggs = 'ftw.recipe.translations'


def main():
    print 'WOHOOO'
