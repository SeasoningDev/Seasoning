from django.db import models
from django.conf import settings
from recipes.models.std import ExternalSite
from recipes.models.recipe import Recipe, Cuisine, UsesIngredient
from django.core.validators import MaxLengthValidator, MinValueValidator
from ingredients.models.ingredients import Ingredient
from ingredients.models.units import Unit
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

class TemporaryIngredientManager(models.Manager):
    
    def get_queryset(self, *args, **kwargs):
        return models.Manager.get_queryset(self, *args, **kwargs).select_related('ingredient')
        
class TemporaryIngredient(models.Model):
    
    objects = TemporaryIngredientManager()
    
    ingredient = models.ForeignKey(Ingredient, null=True, blank=True)
    name = models.CharField(max_length=500)
    
    # Field for existing recipes using an unknown ingredient
    used_by = models.OneToOneField(UsesIngredient, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='temporary_ingredient')
    
    def __unicode__(self):
        if self.ingredient is None or self.ingredient.is_dummy():
            return u'Unknown: {}'.format(self.name)
        
        return self.ingredient.name
           

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
    
    name = models.CharField(_('Name'), max_length=100, default='',
                            help_text=_('The names of the recipe.'),
                            null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='incomplete_recipes')
    
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
    
    description = models.TextField(_('Description'), 
                                   default='',
                                   validators=[MaxLengthValidator(300)],
                                   help_text=_("A few sentences describing the recipe (Maximum 300 characters)."),
                                   null=True, blank=True)
    portions = models.PositiveIntegerField(_('Portions'), default=0,
                                           help_text=_('The average amount of people that can be fed by this recipe '
                                                       'using the given amounts of ingredients.'),
                                           null=True, blank=True)
    active_time = models.IntegerField(_('Active time'), default=0, 
                                      help_text=_('The time needed to prepare this recipe where you are actually doing something.'),
                                      null=True, blank=True)
    passive_time = models.IntegerField(_('Passive time'), default=0, 
                                       help_text=_('The time needed to prepare this recipe where you can do something else (e.g. water is boiling)'),
                                       null=True, blank=True)
    
    ingredients = models.ManyToManyField(TemporaryIngredient, through='TemporaryUsesIngredient', editable=False)
    extra_info = models.TextField(_('Extra info'), default='',
                                  help_text=_('Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")'),
                                  null=True, blank=True)
    instructions = models.TextField(_('Instructions'), default='', 
                                    help_text=_('Detailed instructions for preparing this recipe.'),
                                    null=True, blank=True)
    
    ignore = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name or 'Unnamed recipe by {}'.format(self.author)
    
    def is_temp(self):
        return True
    
    def all_uses_convertible(self):
        for uses in self.uses.select_related('unit__unit').all():
            if not uses.is_convertible():
                return False
        return True
    
    def is_convertible(self):
        """
        Returns True if this temporary recipe has all the necessary information
        to be converted to a real recipe
        
        """
        if self.name and self.author and self.course is not None and self.portions:
            if self.external:
                if self.external_site and self.external_url:
                    return self.all_uses_convertible()
            else:
                if self.instructions:
                    return self.all_uses_convertible()
        return False
    
    def convert(self):
        """
        Converts this temporary recipe to a real recipe if possible
        
        """
        recipe = Recipe(name=self.name, author=self.author, external=self.external, external_url=self.external_url,
                        external_site=self.external_site, course=self.course, cuisine=self.cuisine, 
                        description=self.description, portions=self.portions, active_time=self.active_time,
                        passive_time=self.active_time, extra_info=self.extra_info) 
                    
        recipe.save()
        
        for image in self.images.all():
            image.recipe = recipe
            image.save()
        
        try:
            for t_uses in self.uses.all():
                t_uses.convert(recipe=recipe)
        except (ValueError, Unit.DoesNotExist) as e:
            recipe.uses.all().delete()
            recipe.delete()
            raise e
        
        self.uses.all().delete()
        self.delete()
        
        recipe.recalculate_ingredient_aggregates()
            
        return recipe
    
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
    
    def ingredient_display(self):
        return self.ingredient
    
    def is_convertible(self):
        """
        Returns True if this temporary usesingredient can be converted to
        a real usesingredient
        
        """
        if self.unit.unit is None:
            return False
        if self.ingredient.ingredient is None:
            return True
        return self.ingredient.ingredient.can_use_unit(self.unit.unit)
    
    def convert(self, recipe):
        uses = UsesIngredient(recipe=recipe, ingredient=self.ingredient.ingredient,
                              group=self.group, amount=self.amount, unit=self.unit.unit)
        uses.save(update_recipe_aggregates=False)
        
        self.ingredient.used_by = uses
        self.ingredient.save()
        
        return uses
    
    
    def clean(self, *args, **kwargs):
        # Validate that is ingredient is using a unit that it can use
        if self.ingredient.ingredient is not None and self.ingredient.ingredient.accepted and self.unit.unit is not None:
            if not self.ingredient.ingredient.can_use_unit(self.unit.unit):
                raise ValidationError(_('This unit cannot be used for measuring this Ingredient.'))
        return self
