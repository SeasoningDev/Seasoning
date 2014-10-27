from django.core.management.base import NoArgsCommand
from recipes.models import Recipe, Aggregate
import math

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        Recalculate the denormalized aggregate values of all recipes.
        
        """
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
        print(aor)
        print(sorted_footprints)
        cat_percs = [0.125, 0.25, 0.5, 0.75]
        fp_cats_upper_limits = {}
        for cat_perc, fp_cat in zip(cat_percs, Aggregate.AGGREGATES):
            cutoff_i = int(math.floor(aor*cat_perc))
            print(cutoff_i)
            fp_upper_limit = sorted_footprints[cutoff_i-1]
            fp_cats_upper_limits[fp_cat[0]] = fp_upper_limit
        Aggregate.objects.update_fp_cat_aggregates(fp_cats_upper_limits)