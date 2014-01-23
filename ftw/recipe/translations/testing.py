from plone.testing import Layer
import zc.buildout.testing


class RecipeLayer(Layer):

    @property
    def globs(self):
        # globs is required for zc.buildout.testing setup / tear down
        if 'buildout' not in self:
            self['buildout'] = {}
        return self['buildout']

    def testSetUp(self):
        zc.buildout.testing.buildoutSetUp(self)
        zc.buildout.testing.install_develop('zc.recipe.egg', self)
        zc.buildout.testing.install_develop('ftw.recipe.translations', self)

    def testTearDown(self):
        zc.buildout.testing.buildoutTearDown(self)


RECIPE_FIXTURE = RecipeLayer()
