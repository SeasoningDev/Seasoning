from django.db import models
from django.utils.translation import ugettext_lazy as _
import math
from django.conf import settings

class ExternalSite(models.Model):
    
    name = models.CharField(_('Name'), max_length=200,
                            help_text=_('The names of the external website.'))
    url = models.CharField(_('URL'), max_length=200,
                            help_text=_('The home url of the external website'))
    
    def __unicode__(self):
        return self.name

class AggregateManager(models.Manager):
    
    def recipe_categories(self):
        return self.filter(name__in=[Aggregate.Ap, Aggregate.A, Aggregate.B, Aggregate.C, Aggregate.D])
    
    # See Aggregate class for values of parameter and subset parameters (FOOTPRINT, GLOBAL, VEGANISM, ...)
    # Subset value should be the value of the subset, for example for subset VEGANISM this could be Ingredient.VEGAN
    # or None if not applicable (eg. GLOBAL)
    def get_mean(self, parameter, subset, subset_value):
        return self.get(name=Aggregate.MEAN, extra_info=Aggregate._get_stat_extra_info_field(parameter, subset, subset_value)).value
    
    def get_std_dev(self, parameter, subset, subset_value):
        return self.get(name=Aggregate.STD_DEV, extra_info=Aggregate._get_stat_extra_info_field(parameter, subset, subset_value)).value
    
    def update_fp_categories(self):
        """
        Recalculate the denormalized aggregate values of all recipes.
        
        """
        from recipes.models.recipe import Recipe
        
        recipes = Recipe.objects.all().prefetch_related('uses__unit',
                                                        'uses__ingredient__canuseunit_set__unit',
                                                        'uses__ingredient__available_in_country__location',
                                                        'uses__ingredient__available_in_country__transport_method',
                                                        'uses__ingredient__available_in_sea__location',
                                                        'uses__ingredient__available_in_sea__transport_method')
        footprints = []
        for recipe in recipes:
            recipe.recalculate_ingredient_aggregates()
            if recipe.accepted:
                footprints.append(recipe.footprint)
        
        sorted_footprints = sorted(footprints)
        aor = len(sorted_footprints)
        
        fp_cats_upper_limits = {}
        for cat_perc, fp_cat in zip(settings.RECIPE_CATEGORY_PERCENTAGES, Aggregate.CATEGORIES):
            if cat_perc < 0:
                fp_upper_limit = 1000 * sorted_footprints[aor-1]
            else:
                cutoff_i = int(math.floor(aor*cat_perc))
                fp_upper_limit = sorted_footprints[min(aor-1, cutoff_i-1)]
                
            fp_cats_upper_limits[fp_cat] = fp_upper_limit
            
        for fp_cat, upper_limit in fp_cats_upper_limits.items():
            try:
                aggr = self.get(name=fp_cat)
                aggr.value = upper_limit
                aggr.extra_info = Aggregate.CATEGORIES_TEXT[fp_cat]
                aggr.save()
            except Aggregate.DoesNotExist:
                Aggregate(name=fp_cat, value=upper_limit, extra_info=Aggregate.CATEGORIES_TEXT[fp_cat]).save()
    
    def update_fp_statistics(self):
        from ingredients.models import Ingredient
        from recipes.models import Recipe
        
        all_recipes = []
        veganisms = {veganism[0]: [] for veganism in Ingredient.VEGANISMS}
        courses = {course[0]: [] for course in Recipe.COURSES}
        
        for recipe in Recipe.objects.all():
            all_recipes.append(recipe)
            veganisms[recipe.veganism].append(recipe)
            courses[recipe.course].append(recipe)
            
        aor = len(all_recipes)
        mean = sum([recipe.footprint for recipe in all_recipes]) / aor
        std_dev = math.sqrt(sum([(recipe.footprint - mean)**2 for recipe in all_recipes]) / aor)
        Aggregate.objects.update_or_create(name=Aggregate.MEAN, extra_info=Aggregate._get_stat_extra_info_field(Aggregate.FOOTPRINT, Aggregate.GLOBAL, None),
                  defaults={'value': mean})
        Aggregate.objects.update_or_create(name=Aggregate.STD_DEV, extra_info=Aggregate._get_stat_extra_info_field(Aggregate.FOOTPRINT, Aggregate.GLOBAL, None),
                  defaults={'value': std_dev})
                  
        for veg, recipes in veganisms.items():
            aor = len(recipes)
            if aor <= 0:
                continue
            mean = sum([recipe.footprint for recipe in recipes]) / aor
            std_dev = math.sqrt(sum([(recipe.footprint - mean)**2 for recipe in recipes]) / aor)
            Aggregate.objects.update_or_create(name=Aggregate.MEAN, extra_info=Aggregate._get_stat_extra_info_field(Aggregate.FOOTPRINT, Aggregate.VEGANISM, veg),
                      defaults={'value': mean})
            Aggregate.objects.update_or_create(name=Aggregate.STD_DEV, extra_info=Aggregate._get_stat_extra_info_field(Aggregate.FOOTPRINT, Aggregate.VEGANISM, veg),
                      defaults={'value': std_dev})
                  
        for course, recipes in courses.items():
            aor = len(recipes)
            if aor <= 0:
                continue
            mean = sum([recipe.footprint for recipe in recipes]) / aor
            std_dev = math.sqrt(sum([(recipe.footprint - mean)**2 for recipe in recipes]) / aor)
            Aggregate.objects.update_or_create(name=Aggregate.MEAN, extra_info=Aggregate._get_stat_extra_info_field(Aggregate.FOOTPRINT, Aggregate.COURSE, course),
                      defaults={'value': mean})
            Aggregate.objects.update_or_create(name=Aggregate.STD_DEV, extra_info=Aggregate._get_stat_extra_info_field(Aggregate.FOOTPRINT, Aggregate.COURSE, course),
                      defaults={'value': std_dev})
    
class Aggregate(models.Model):
    Ap, A, B, C, D = 0, 1, 2, 3, 4
    CATEGORIES = [Ap, A, B, C, D]
    CATEGORIES_DICT = {Ap: 'A+', A: 'A', B: 'B', C: 'C', D: 'D'}
    CATEGORIES_TEXT = {Ap: 'De voetafdruk van dit recept is lager dan 90% van de recepten op Seasoning',
                       A: 'De voetadruk van dit recept is lager dan 75% van de recepten op Seasoning',
                       B: 'De voetafdruk van dit recept is lager dan 50% van de recepten op Seasoning',
                       C: 'De voetafdruk van dit recept is hoger dan 50% van de recepten op Seasoning',
                       D: 'De voetafdruk van dit recept is hoger dan 75% van de recepten op Seasoning'}
    
    MEAN, STD_DEV = 5, 6
    STATISTICS = ((MEAN, 'Mean Value'), (STD_DEV, 'Standard Deviation'))
    # Parameters of which statistical data is collected
    FOOTPRINT = 1
    # Subsets of recipes from which statistical data is collected
    GLOBAL, VEGANISM, COURSE = 'g', 'v', 'c'
    
    AGGREGATES = [(cat, CATEGORIES_DICT[cat]) for cat in [Ap, A, B, C, D]]
    AGGREGATES.extend(STATISTICS)
    
    objects = AggregateManager()
    name = models.PositiveSmallIntegerField(choices=AGGREGATES)
    value = models.FloatField()
    extra_info = models.CharField(max_length=100, default='')
    
    class Meta:
        unique_together = (('name', 'extra_info'),)
    
    @classmethod
    def _get_stat_extra_info_field(cls, param, subset, subset_val):
        return '{}{}{}'.format(param, subset, subset_val or '')
    
    def __unicode__(self):
        if self.extra_info:
            return '{} - {} ({})'.format(self.get_name_display(), self.extra_info, self.value)
        return '{} ({})'.format(self.get_name_display(), self.value)
    
    def get_ribbon_image_name(self):
        return 'cat-ribbon-{0}.png'.format(self.get_name_display())
    