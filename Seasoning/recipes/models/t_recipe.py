from django.db import models
from django.conf import settings
from recipes.models.std import ExternalSite
from recipes.models.recipe import Recipe, Cuisine
from django.core.validators import MaxLengthValidator, MinValueValidator
from ingredients.models.ingredients import Ingredient
from ingredients.models.units import Unit
from django.utils.translation import ugettext_lazy as _

class TemporaryIngredientManager(models.Manager):
    
    def get_queryset(self, *args, **kwargs):
        return models.Manager.get_queryset(self, *args, **kwargs).select_related('ingredient')
        
class TemporaryIngredient(models.Model):
    
    objects = TemporaryIngredientManager()
    
    ingredient = models.ForeignKey(Ingredient, null=True, blank=True)
    name = models.CharField(max_length=500)
    
    def __unicode__(self):
        if self.ingredient is not None:
            return self.ingredient.name
           
        return u'Unknown: {}'.format(self.name)

class TemporaryUnitManager(models.Manager):
    
    def get_queryset(self, *args, **kwargs):
        return models.Manager.get_queryset(self, *args, **kwargs).select_related('unit')
    
class TemporaryUnit(models.Model):
    objects = TemporaryUnitManager()
    
    unit = models.ForeignKey(Unit, null=True, blank=True)
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        if self.unit is not None:
            return self.unit.name
         
        return u'Unknown: {}'.format(self.name)
    

class IncompleteRecipe(models.Model):
    
    name = models.CharField(_('Name'), max_length=100,
                            help_text=_('The names of the recipe.'),
                            null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='incomplete_recipes', null=True)
    
    external = models.BooleanField(default=False)
    external_url = models.CharField(max_length=1000, null=True, blank=True)
    external_site = models.ForeignKey(ExternalSite, related_name='incomplete_recipes',
                                      null=True, blank=True)
    
    course = models.PositiveSmallIntegerField(_('Course'), choices=Recipe.COURSES,
                                              help_text=_("The type of course this recipe will provide."),
                                              null=True, blank=True)
    cuisine = models.ForeignKey(Cuisine, verbose_name=_('Cuisine'), db_column='cuisine',
                                help_text=_("The type of cuisine this recipe represents."), 
                                null=True, blank=True)
    cuisine_proposal = models.CharField(max_length=50, null=True, blank=True)
    
    description = models.TextField(_('Description'), validators=[MaxLengthValidator(300)],
                                   help_text=_("A few sentences describing the recipe (Maximum 300 characters)."),
                                   null=True, blank=True)
    portions = models.PositiveIntegerField(_('Portions'), help_text=_('The average amount of people that can be fed by this recipe '
                                                       'using the given amounts of ingredients.'),
                                           null=True, blank=True)
    active_time = models.IntegerField(_('Active time'), help_text=_('The time needed to prepare this recipe where you are actually doing something.'),
                                      null=True, blank=True)
    passive_time = models.IntegerField(_('Passive time'), help_text=_('The time needed to prepare this recipe where you can do something else (e.g. water is boiling)'),
                                       null=True, blank=True)
    
    ingredients = models.ManyToManyField(TemporaryIngredient, through='TemporaryUsesIngredient', editable=False)
    extra_info = models.TextField(_('Extra info'), default='',
                                  help_text=_('Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")'),
                                  null=True, blank=True)
    instructions = models.TextField(_('Instructions'), help_text=_('Detailed instructions for preparing this recipe.'),
                                    null=True, blank=True)
    
    ignore = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
    
    def incomplete_class(self):
        return True
    
    def course_ok(self):
        return self.course is not None
    
    def cuisine_ok(self):
        return self.cuisine is not None
     

    
class TemporaryUsesIngredient(models.Model):
    
    recipe = models.ForeignKey(IncompleteRecipe, related_name='uses', db_column='recipe')
    ingredient = models.ForeignKey(TemporaryIngredient, related_name='used_in', db_column='ingredient')
    
    group = models.CharField(max_length=100, blank=True)
    amount = models.FloatField(default=0, validators=[MinValueValidator(0.00001)])
    unit = models.ForeignKey(TemporaryUnit, db_column='unit')
