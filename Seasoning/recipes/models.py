import time
import ingredients
from django.db import models
from django.core.validators import MinValueValidator,\
    MaxLengthValidator
from django.db.models.fields import FloatField
from django.utils.translation import ugettext_lazy as _
from imagekit.models.fields import ProcessedImageField, ImageSpecField
from imagekit.processors.resize import SmartResize
from ingredients.models import CanUseUnit
import math

def get_image_filename(instance, old_filename):
    extension = old_filename.split('.')[-1]
    filename = '%s.%s' % (str(time.time()), extension)
    return 'images/recipes/' + filename

class Cuisine(models.Model):
    
    class Meta:
        ordering = ["name"]
    
    name = models.CharField(max_length=50)

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
    description = models.TextField(_('Description'), validators=[MaxLengthValidator(140)],
                                   help_text=_("A few sentences describing the recipe (Maximum 140 characters)."))
    portions = models.PositiveIntegerField(_('Portions'), help_text=_('The average amount of people that can be fed by this recipe '
                                                       'using the given amounts of ingredients.'))
    active_time = models.IntegerField(_('Active time'), help_text=_('The time needed to prepare this recipe where you are actually doing something.'))
    passive_time = models.IntegerField(_('Passive time'), help_text=_('The time needed to prepare this recipe where you can do something else (e.g. water is boiling)'))
    
    ingredients = models.ManyToManyField(ingredients.models.Ingredient, through='UsesIngredient', editable=False)
    extra_info = models.TextField(_('Extra info'), default='', blank=True,
                                  help_text=_('Extra info about the ingredients or needed tools (e.g. "You will need a mixer for this recipe" or "Use big potatoes")'))
    instructions = models.TextField(_('Instructions'), help_text=_('Detailed instructions for preparing this recipe.'))
    
    image = ProcessedImageField(upload_to=get_image_filename,
                                help_text=_('An image of this recipe. Please do not use copyrighted images, these will be removed as quick as possible.'))
    thumbnail = ImageSpecField([SmartResize(216, 216)], source='image', format='JPEG')
    small_image = ImageSpecField([SmartResize(310, 310)], source='image', format='JPEG')
    
    def footprint(self):
        total_footprint = 0
        for uses_ingredient in self.uses_ingredient.all():
            total_footprint += uses_ingredient.footprint()
            
        return total_footprint
    
    def footprint_category(self, display=False):
        distribution_parameters = RecipeDistribution.objects.filter(course=self.course)
        
        mean = list(filter(lambda x: x.parameter == RecipeDistribution.MEAN, distribution_parameters))[0].value
        std = list(filter(lambda x: x.parameter == RecipeDistribution.STANDARD_DEVIATION, distribution_parameters))[0].value
        
        for cat, cat_display in self.FOOTPRINT_CATEGORIES:
            probit_val = mean + (std * math.sqrt(2) * RecipeDistribution.IERF[self.FOOTPRINT_CATEGORY_CUTOFF_VALUES[cat]])
            
            if self.footprint() <= probit_val:
                if display:
                    return cat_display
                return cat
    
    def get_footprint_category_display(self):
        return self.footprint_category(display=True)
        
    

class UsesIngredient(models.Model):
    
    recipe = models.ForeignKey(Recipe, related_name='uses_ingredient')
    ingredient = models.ForeignKey(ingredients.models.Ingredient)
    
    group = models.CharField(max_length=100, blank=True)
    amount = models.FloatField(default=0, validators=[MinValueValidator(0.00001)])
    unit = models.ForeignKey(ingredients.models.Unit)
    
    def unit_conversion_ratio(self):
        if self.unit.parent_unit is not None:
            return CanUseUnit.objects.get(ingredient=self.ingredient, unit=self.unit.parent_unit).conversion_ratio * self.unit.ratio
            
        return CanUseUnit.objects.get(ingredient=self.ingredient, unit=self.unit).conversion_ratio
    
    def footprint(self):
        return self.ingredient.footprint() * self.amount * self.unit_conversion_ratio()



class RecipeDistribution(models.Model):
    
    MEAN, STANDARD_DEVIATION = 0, 1
    DISTRIBUTION_PARAMETERS = ((MEAN, _('Gemiddelde')), (STANDARD_DEVIATION, _('Standaardafwijking')))
    
    # Inverse Error function values
    IERF = {0.1: -0.90619380,
            0.25: -0.47693628,
            0.5: 0,
            0.75: 0.47693628,
            1: 100000}
    
    course = models.PositiveSmallIntegerField(choices=Recipe.COURSES)
    parameter = models.PositiveSmallIntegerField(choices=DISTRIBUTION_PARAMETERS)
    
    value = models.FloatField()
    
    class Meta:
        unique_together = (('course', 'parameter'), )
    
    
    