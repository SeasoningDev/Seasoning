import time
import ingredients
from django.db import models
from django.core.validators import MinValueValidator,\
    MaxLengthValidator
from django.utils.translation import ugettext_lazy as _
from imagekit.models.fields import ProcessedImageField, ImageSpecField
from imagekit.processors.resize import SmartResize
from ingredients.models import Unit, Ingredient
import math
from django.core.exceptions import ValidationError
import urllib
from django.core.files.base import File
from markitup.fields import MarkupField
from tempfile import NamedTemporaryFile
from django.utils import timezone
from datetime import timedelta

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
    
    def __str__(self):
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
    
    name = models.CharField(_('Name'), max_length=300,
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
    instructions = MarkupField(_('Instructions'), null=True, blank=True,
                               help_text=_('Detailed instructions for preparing this recipe.'))
    
    image = ProcessedImageField(upload_to=get_image_filename,
                                help_text=_('An image of this recipe. Please do not use copyrighted images, these will be removed as quick as possible.'))
    image_normal = ImageSpecField([SmartResize(400, 400)], source='image', format='JPEG')
    image_thumbnail = ImageSpecField([SmartResize(248, 348)], source='image', format='JPEG')

    
    
    time_added = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)
    
    
    """
    Cached attributes, be very carefull when using these, might be out of sync
    
    """
    cached_veganism = models.PositiveSmallIntegerField(choices=Ingredient.VEGANISMS, null=True, blank=True)
    cached_footprint = models.FloatField(null=True, blank=True)
    cached_in_season = models.BooleanField(default=False)
    cached_has_endangered_ingredients = models.BooleanField(default=False)
    cached_footprint_category = models.PositiveSmallIntegerField(choices=FOOTPRINT_CATEGORIES)
    
    def __str__(self):
        return self.name
    
    
    
    def veganism(self):
        return min(ingredient.veganism for ingredient in self.ingredients.all())
    
    def total_footprint(self, date=None):
        total_footprint = 0
        for uses_ingredient in self.uses_ingredients.all():
            total_footprint += uses_ingredient.footprint(date)
            
        return total_footprint
    
    def normalized_footprint(self, date=None):
        return self.total_footprint(date) / self.portions
    
    def in_season(self, date=None):
        return any(ingredient.type is not Ingredient.BASIC for ingredient in self.ingredients.all()) and \
            all(ingredient.is_in_season(date) for ingredient in self.ingredients.all())
    
    def has_endangered_ingredients(self, date=None):
        return any(ingredient.is_endangered(date) for ingredient in self.ingredients.all())
    
    def update_cached_attributes(self):
        self.uses_ingredients.select_related('ingredient__can_use_units__unit',
                                                         'unit__parent_unit').all()
        self.cached_veganism = self.veganism()
        self.cached_footprint = self.normalized_footprint()
        self.cached_in_season = self.in_season()
        self.cached_has_endangered_ingredients = self.has_endangered_ingredients()
        self.cached_footprint_category = self.footprint_category()
        
        self.save()
        

    _recipe_distributions_cache = None
    _recipe_distributions_cache_since = None
    def recipe_distribution_parameters(self, course):
        if self._recipe_distributions_cache is None or self._recipe_distributions_cache_since is None or \
           self._recipe_distributions_cache_since < timezone.now() - timedelta(days=1):
            self.__class__._recipe_distributions_cache = RecipeDistribution.objects.all()
            self.__class__._recipe_distributions_cache_since = timezone.now()
        
        return list(filter(lambda x: x.group == course, self._recipe_distributions_cache))
    
    def footprint_category(self, display=False):
        distribution_parameters = self.recipe_distribution_parameters(self.course)
        
        try:
            mean = list(filter(lambda x: x.parameter == RecipeDistribution.MEAN, distribution_parameters))[0].parameter_value
        except IndexError:
            mean = 0
        
        try:
            std = list(filter(lambda x: x.parameter == RecipeDistribution.STANDARD_DEVIATION, distribution_parameters))[0].parameter_value
        except IndexError:
            std = 0
        
        for cat, cat_display in self.FOOTPRINT_CATEGORIES:
            probit_val = mean + (std * math.sqrt(2) * RecipeDistribution.IERF[self.FOOTPRINT_CATEGORY_CUTOFF_VALUES[cat]])
            
            if self.cached_footprint <= probit_val:
                if display:
                    return cat_display
                return cat
        
        last_cat = self.FOOTPRINT_CATEGORIES[-1]
        
        return last_cat[0] if not display else last_cat[1] 
    
    def get_footprint_category_display(self):
        return self.footprint_category(display=True)
        
    

class UsesIngredient(models.Model):
    
    recipe = models.ForeignKey(Recipe, related_name='uses_ingredients')
    ingredient = models.ForeignKey(ingredients.models.Ingredient)
    
    group = models.CharField(max_length=100, null=True, blank=True)
    amount = models.FloatField(default=0, validators=[MinValueValidator(0.00001)])
    unit = models.ForeignKey(ingredients.models.Unit)
    
    def __str__(self):
        return 'Recipe {} uses Ingredient {}'.format(self.recipe_id, self.ingredient_id)
    
    def get_unit_display(self):
        if self.amount == 1:
            return self.unit.get_display_name()
        
        return self.unit.get_display_name_plural()
    
    def get_ingredient_display(self):
        if self.amount == 1 or self.ingredient.plural_name is None or self.ingredient.plural_name == '':
            return self.ingredient.name
        
        return self.ingredient.plural_name
    
    
    
    
    
    def unit_conversion_ratio(self):
        if self.unit.parent_unit is not None:
            return next(cuu for cuu in self.ingredient.can_use_units.all() if cuu.unit == self.unit.parent_unit).conversion_ratio * self.unit.ratio
            
        return next(cuu for cuu in self.ingredient.can_use_units.all() if cuu.unit == self.unit).conversion_ratio
    
    def footprint(self, date=None):
        return self.ingredient.footprint(date) * self.amount * self.unit_conversion_ratio()
    
    def footprint_breakdown(self, date=None):
        return {footprint_source: footprint * self.amount * self.unit_conversion_ratio() for footprint_source, footprint in self.ingredient.footprint_breakdown(date).items()}
    
    
    
    def clean(self):
        if self.unit is not None and self.ingredient is not None:
            if self.unit.parent_unit is None:
                unit = self.unit
            else:
                unit = self.unit.parent_unit
            
            if not unit in [cuu.unit for cuu in self.ingredient.can_use_units.all()]:
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
    
    
    ALL = 100
    GROUPS = [(ALL, _('All Recipes'))]
    GROUPS.extend(Recipe.COURSES)
    
    group = models.PositiveSmallIntegerField(choices=GROUPS)
    parameter = models.PositiveSmallIntegerField(choices=DISTRIBUTION_PARAMETERS)
    
    parameter_value = models.FloatField()
    
    class Meta:
        unique_together = (('group', 'parameter'), )
        
    
    """
    Here we provide functions for the statistical analysis of recipe footprint.
    We make the following assumptions:
        * The footprints of recipes follow a normal distribution
        * The footprint of a recipe can only be compared to other recipes of the
          same course type
    
    To find the footprint category of a recipe, we need to calculate a footprint
    that is smaller than p% of all the footprints.
    
    The probit function PHI-1(p) yields a value for which the probablity is p that
    any other value will be smaller or equal to it. So PHI-1(0.1) gives us the 
    10% quantile footprint.
    
    However, since our distribution go into the negative part of the axes, and
    negative footprints are not possible, we need to take into account that this
    part of the distribution doesn't exist.
    
    As such we have:
    PHI(0): The theorethical probability that a footprint will have a value lower
            than 0, call this p_0
    1 - p_0: The theorethical probability that a footprint will be higher than 0,
             call this p_1
    
    This means that to find PHI-1(0.1), we actually have to find PHI-1(p_0 + (0.1 * p_1))
    
    For ease of calculation, we will approximate the normal distribution N(x) with the 
    logistic distribution L(x). To achieve a comparable logistic distribution, we need a
    scaling factor so that N(0, m, s) = l_0 * L(0, m, s)
    
    """
    @classmethod
    def logistic(cls, x, mean, std, scaling=1):
        return scaling * (math.exp(-(x - mean) / std) / (std * math.pow((1 + math.exp(-(x - mean) / std)), 2)))
    
#     @classmethod
#     def logistic_cdf(cls, x, mean, std, scaling=1):
#         
    
    @classmethod
    def distribution_scaling_factor(cls, mean, std):
        N_0 = 1 / (std * math.sqrt(2 * math.pi))
        L_0 = cls.logistic(0, mean, std)
        
        return N_0 / L_0
    
    
        
        
    
    
    def __str__(self):
        return '{} of `{}` courses is {:.2f}'.format(self.get_parameter_display(), self.get_group_display(), self.parameter_value)
    
  
  
  
    
class ScrapedRecipe(models.Model):
    
    class Meta:
        unique_together = (('scraped_name', 'external_site'), )
    
    name = models.CharField(_('Name'), max_length=300, default='',
                            help_text=_('The name of the recipe.'),
                            null=True, blank=True)
    
    scraped_name = models.CharField(_('Scraped Name'), max_length=300, null=True, blank=True)
    
    external = models.BooleanField(default=False)
    external_url = models.CharField(max_length=1000, null=True, blank=True)
    external_site = models.ForeignKey(ExternalSite, related_name='incomplete_recipes',
                                      null=True, blank=True)
    
    course = models.PositiveSmallIntegerField(_('Course'), choices=Recipe.COURSES,
                                              help_text=_("The type of course this recipe will provide."),
                                              null=True, blank=True)
    course_proposal = models.CharField(max_length=100, null=True, blank=True)
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
    
    def __str__(self):
        return '{}: {}'.format(self.external_site.name, self.name)
    
    
    
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
    
    def ao_unfinished_ingredients(self):
        if not hasattr(self, '_ao_unfinished_ingredients') or getattr(self, '_ao_unfinished_ingredients') is None:
            setattr(self, '_ao_unfinished_ingredients', len(list(filter(lambda ing: ing.ingredient is None or not ing.ingredient.accepted, self.ingredients.all()))))
            
        return getattr(self, '_ao_unfinished_ingredients')
    
    def ao_unknown_ingredients(self):
        if not hasattr(self, '_ao_unknown_ingredients') or getattr(self, '_ao_unknown_ingredients') is None:
            setattr(self, '_ao_unknown_ingredients', len(list(filter(lambda ing: ing.ingredient is None, self.ingredients.all()))))
            
        return getattr(self, '_ao_unknown_ingredients')
    
    
    def convert_to_real_recipe(self):
        if self.is_missing_info():
            raise ValidationError('The recipe `{}` cannot be converted while it is missing required info'.format(self.name))
        
        for ingredient in self.ingredients.all():
            ingredient.clean()
            
        img_temp = NamedTemporaryFile(delete=True, suffix='.jpg')
        img_temp.write(urllib.request.urlopen(self.image_url).read())
        img_temp.flush()
        
        real_recipe = Recipe(name=self.name,
                             external=True, external_site=self.external_site, external_url=self.external_url,
                             course=self.course, cuisine=self.cuisine, description=self.description, portions=self.portions,
                             image=File(img_temp), instructions='')
        
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
    ingredient_proposal = models.CharField(max_length=500)
    
    group = models.CharField(max_length=500, null=True, blank=True)
    amount = models.FloatField(default=0, validators=[MinValueValidator(0.00001)], null=True, blank=True)
    amount_proposal = models.CharField(max_length=20, null=True, blank=True)
    
    unit = models.ForeignKey(Unit, null=True, blank=True)
    unit_proposal = models.CharField(max_length=50, null=True, blank=True)
    
    def clean(self):
        if self.unit is not None and self.ingredient is not None:
            if not self.ingredient.can_use_unit(self.unit):
                raise ValidationError('Ingredient `{}` can not use unit `{}`'.format(self.ingredient, self.unit))
            
