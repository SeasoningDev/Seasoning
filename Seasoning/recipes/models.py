import time
import ingredients
from django.db import models
from django.core.validators import MinValueValidator,\
    MaxLengthValidator
from django.db.models.fields import FloatField
from django.utils.translation import ugettext_lazy as _
from imagekit.models.fields import ProcessedImageField, ImageSpecField
from imagekit.processors.resize import SmartResize
from ingredients.models import CanUseUnit, Unit, Ingredient
import math
from django.core.exceptions import ValidationError
from django.core.files.temp import NamedTemporaryFile
import urllib
from django.core.files.base import File

def get_image_filename(instance, old_filename):
    extension = old_filename.split('.')[-1]
    print(old_filename)
    filename = '%s.%s' % (str(time.time()), extension)
    return 'images/recipes/' + filename

class Cuisine(models.Model):
    
    class Meta:
        ordering = ["name"]
    
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
    

class ExternalSite(models.Model):
    
    name = models.CharField(_('Name'), max_length=200,
                            help_text=_('The name of the external website.'))
    url = models.CharField(_('URL'), max_length=200,
                            help_text=_('The home url of the external website'))
    
    def __unicode__(self):
        return self.name

class Recipe(models.Model):
    
    ENTRY, BREAD, BREAKFAST, DESERT, DRINK, MAIN_COURSE, SALAD, SIDE_DISH, SOUP, MARINADE_AND_SAUCE = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
    COURSES = ((ENTRY,u'Voorgerecht'),
               (BREAD,u'Brood'),
               (BREAKFAST,u'Ontbijt'),
               (DESERT,u'Dessert'),
               (DRINK,u'Drank'),
               (MAIN_COURSE,u'Hoofdgerecht'),
               (SALAD,u'Salade'),
               (SIDE_DISH,u'Bijgerecht'),
               (SOUP,u'Soep'),
               (MARINADE_AND_SAUCE,u'Marinades en sauzen'))
    
    Ap, A, B, C, D = 0, 1, 2, 3, 4
    FOOTPRINT_CATEGORIES = ((Ap, 'A+'), (A, 'A'), (B, 'B'), (C, 'C'), (D, 'D'))
    FOOTPRINT_CATEGORY_CUTOFF_VALUES = {Ap: 0.1,
                                        A: 0.25,
                                        B: 0.5,
                                        C: 0.75,
                                        D: 1}
    
    name = models.CharField(_('Name'), max_length=100,
                            help_text=_('The names of the recipe.'))
    
    external = models.BooleanField(default=False)
    external_url = models.CharField(max_length=1000, null=True, blank=True)
    external_site = models.ForeignKey(ExternalSite, null=True, blank=True)
    
    course = models.PositiveSmallIntegerField(_('Course'), choices=COURSES,
                                              help_text=_("The type of course this recipe will provide."))
    cuisine = models.ForeignKey(Cuisine, verbose_name=_('Cuisine'), null=True, blank=True,
                                help_text=_("The type of cuisine this recipe represents."))
    description = models.TextField(_('Description'), validators=[MaxLengthValidator(140)], null=True, blank=True,
                                   help_text=_("A few sentences describing the recipe (Maximum 140 characters)."))
    portions = models.PositiveIntegerField(_('Portions'), help_text=_('The average amount of people that can be fed by this recipe '
                                                       'using the given amounts of ingredients.'))
    active_time = models.IntegerField(_('Active time'), help_text=_('The time needed to prepare this recipe where you are actually doing something.'), null=True, blank=True)
    passive_time = models.IntegerField(_('Passive time'), help_text=_('The time needed to prepare this recipe where you can do something else (e.g. water is boiling)'), null=True, blank=True)
    
    ingredients = models.ManyToManyField(ingredients.models.Ingredient, through='UsesIngredient', editable=False)
    extra_info = models.TextField(_('Extra info'), default='', blank=True,
                                  help_text=_('Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")'))
    instructions = models.TextField(_('Instructions'), null=True, blank=True,
                                    help_text=_('Detailed instructions for preparing this recipe.'))
    
    image = ProcessedImageField(upload_to=get_image_filename,
                                help_text=_('An image of this recipe. Please do not use copyrighted images, these will be removed as quick as possible.'))
    thumbnail = ImageSpecField([SmartResize(216, 216)], source='image', format='JPEG')
    small_image = ImageSpecField([SmartResize(310, 310)], source='image', format='JPEG')
    
    
    
    time_added = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)
    
    
    """
    Cached attributes, be very carefull when using these, might be out of sync
    
    """
    _veganism = models.PositiveSmallIntegerField(choices=Ingredient.VEGANISMS, null=True, blank=True)
    _footprint = models.FloatField(null=True, blank=True)
    _in_season = models.BooleanField(default=False)
    _has_endangered_ingredients = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    
    
    def veganism(self):
        return min(ingredient.veganism for ingredient in self.ingredients.all())
    
    
    
    def total_footprint(self):
        total_footprint = 0
        for uses_ingredient in self.uses_ingredients.all():
            total_footprint += uses_ingredient.footprint()
            
        return total_footprint
    
    def normalized_footprint(self):
        return self.total_footprint() / self.portions
    
    def footprint_category(self, display=False):
        distribution_parameters = RecipeDistribution.objects.filter(course=self.course)
        
        try:
            mean = list(filter(lambda x: x.parameter == RecipeDistribution.MEAN, distribution_parameters))[0].value
        except IndexError:
            mean = 0
        
        try:
            std = list(filter(lambda x: x.parameter == RecipeDistribution.STANDARD_DEVIATION, distribution_parameters))[0].value
        except IndexError:
            std = 0
        
        for cat, cat_display in self.FOOTPRINT_CATEGORIES:
            probit_val = mean + (std * math.sqrt(2) * RecipeDistribution.IERF[self.FOOTPRINT_CATEGORY_CUTOFF_VALUES[cat]])
            
            if self.normalized_footprint() <= probit_val:
                if display:
                    return cat_display
                return cat
    
    def get_footprint_category_display(self):
        return self.footprint_category(display=True)
    
    
    
    def update_cached_attributes(self):
        self.uses_ingredients.select_related('ingredient__can_use_units__unit',
                                                         'unit__parent_unit').all()
        self._veganism = self.veganism()
        self._footprint = self.normalized_footprint()
        self._in_season = False
        self._has_endangered_ingredients = False
        
        self.save()
        
    

class UsesIngredient(models.Model):
    
    recipe = models.ForeignKey(Recipe, related_name='uses_ingredients')
    ingredient = models.ForeignKey(ingredients.models.Ingredient)
    
    group = models.CharField(max_length=100, blank=True)
    amount = models.FloatField(default=0, validators=[MinValueValidator(0.00001)])
    unit = models.ForeignKey(ingredients.models.Unit)
    
    def unit_conversion_ratio(self):
        if self.unit.parent_unit is not None:
            return next(cuu for cuu in self.ingredient.can_use_units.all() if cuu.unit == self.unit.parent_unit).conversion_ratio * self.unit.ratio
            
        return next(cuu for cuu in self.ingredient.can_use_units.all() if cuu.unit == self.unit).conversion_ratio
    
    def footprint(self):
        return self.ingredient.footprint() * self.amount * self.unit_conversion_ratio()
    
    
    
    def clean(self):
        if self.unit is not None and self.ingredient is not None:
            if self.unit.parent_unit is None:
                if not CanUseUnit.objects.filter(ingredient=self.ingredient, unit=self.unit).exists():
                    raise ValidationError('Ingredient `{}` can not use unit `{}`'.format(self.ingredient, self.unit))
            
            else:
                if not CanUseUnit.objects.filter(ingredient=self.ingredient, unit=self.unit.parent_unit).exists():
                    raise ValidationError('Ingredient `{}` can not use unit `{}`'.format(self.ingredient, self.unit))



class RecipeDistribution(models.Model):
    
    MEAN, STANDARD_DEVIATION = 0, 1
    DISTRIBUTION_PARAMETERS = ((MEAN, _('Mean')), (STANDARD_DEVIATION, _('Standard Deviation')))
    
    # Inverse Error function values
    IERF = {0.1: -0.90619380,
            0.25: -0.47693628,
            0.5: 0,
            0.75: 0.47693628,
            1: 100000}
    
    course = models.PositiveSmallIntegerField(choices=Recipe.COURSES)
    parameter = models.PositiveSmallIntegerField(choices=DISTRIBUTION_PARAMETERS)
    
    parameter_value = models.FloatField()
    
    class Meta:
        unique_together = (('course', 'parameter'), )
        
    
    
    def __str__(self):
        return '{} of `{}` courses is {:.2f}'.format(self.get_parameter_display(), self.get_course_display(), self.parameter_value)
    
  
  
  
    
class ScrapedRecipe(models.Model):
    
    name = models.CharField(_('Name'), max_length=100, default='',
                            help_text=_('The names of the recipe.'),
                            null=True, blank=True)
    
    external = models.BooleanField(default=False)
    external_url = models.CharField(max_length=1000, null=True, blank=True)
    external_site = models.ForeignKey(ExternalSite, related_name='incomplete_recipes',
                                      null=True, blank=True)
    
    course = models.PositiveSmallIntegerField(_('Course'), choices=Recipe.COURSES,
                                              help_text=_("The type of course this recipe will provide."),
                                              null=True, blank=True)
    course_proposal = models.CharField(max_length=50, null=True, blank=True)
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
    
    extra_info = models.TextField(_('Extra info'), default='',
                                  help_text=_('Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")'),
                                  null=True, blank=True)
    instructions = models.TextField(_('Instructions'), default='', 
                                    help_text=_('Detailed instructions for preparing this recipe.'),
                                    null=True, blank=True)
    
    ignore = models.BooleanField(default=False)
    
    image_url = models.URLField(max_length=400, null=True, blank=True)
    
    first_scrape_date = models.DateField(auto_now_add=True)
    last_update_date = models.DateField(auto_now=True)
    
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    
    deleted = models.BooleanField(default=False)
    
    def is_missing_info(self):
        if not hasattr(self, '_is_missing_info') or getattr(self, '_is_missing_info') is None:
            if self.course is None:
                _is_missing_info = True
            elif len(list(filter(lambda ing: ing.ingredient is None or not ing.ingredient.accepted or ing.unit is None or ing.amount is None, self.ingredients.all()))) > 0:
                _is_missing_info = True
            else:
                _is_missing_info = False
            setattr(self, '_is_missing_info', _is_missing_info)
    
        return getattr(self, '_is_missing_info')
    
    def ao_unknown_ingredients(self):
        if not hasattr(self, '_ao_unknown_ingredients') or getattr(self, '_ao_unknown_ingredients') is None:
            setattr(self, '_ao_unknown_ingredients', len(list(filter(lambda ing: ing.ingredient is None, self.ingredients.all()))))
            
        return getattr(self, '_ao_unknown_ingredients')
    
    
    def convert_to_real_recipe(self):
        if self.is_missing_info():
            raise ValidationError('The recipe `{}` cannot be converted while it is missing required info'.format(self.name))
        
        for ingredient in self.ingredients.all():
            try:
                CanUseUnit.objects.get(ingredient=ingredient.ingredient, unit=ingredient.unit)
            except CanUseUnit.DoesNotExist:
                raise ValidationError('The ingredient `{}` can not use unit `{}`.'.format(ingredient.ingredient, ingredient.unit))
            
        img_temp = NamedTemporaryFile(delete=True, suffix='.jpg')
        img_temp.write(urllib.request.urlopen(self.image_url).read())
        img_temp.flush()
        
        real_recipe = Recipe(name=self.name,
                             external=True, external_site=self.external_site, external_url=self.external_url,
                             course=self.course, cuisine=self.cuisine, description=self.description, portions=self.portions,
                             image=File(img_temp))
        
        real_recipe.save()
        
        for uses_ingredient in self.ingredients.all():
            UsesIngredient(recipe=real_recipe, ingredient=uses_ingredient.ingredient, amount=uses_ingredient.amount,
                           unit=uses_ingredient.unit, group=uses_ingredient.group).save()
        
        real_recipe.update_cached_attributes()
        
        self.recipe = real_recipe
        self.save()
     

    
class ScrapedUsesIngredient(models.Model):
    
    recipe = models.ForeignKey(ScrapedRecipe, related_name='ingredients')
    
    ingredient = models.ForeignKey(Ingredient, null=True, blank=True)
    ingredient_proposal = models.CharField(max_length=100)
    
    group = models.CharField(max_length=100, blank=True)
    amount = models.FloatField(default=0, validators=[MinValueValidator(0.00001)], null=True, blank=True)
    amount_proposal = models.FloatField(default=0, validators=[MinValueValidator(0.00001)], null=True, blank=True)
    
    unit = models.ForeignKey(Unit, null=True, blank=True)
    unit_proposal = models.CharField(max_length=50, null=True, blank=True)
    
    def clean(self):
        if self.unit is not None and self.ingredient is not None:
            if self.unit.parent_unit is None:
                if not CanUseUnit.objects.filter(ingredient=self.ingredient, unit=self.unit).exists():
                    raise ValidationError('Ingredient `{}` can not use unit `{}`'.format(self.ingredient, self.unit))
            
            else:
                if not CanUseUnit.objects.filter(ingredient=self.ingredient, unit=self.unit.parent_unit).exists():
                    raise ValidationError('Ingredient `{}` can not use unit `{}`'.format(self.ingredient, self.unit))
