from django.core.management.base import NoArgsCommand
from recipes.models import Recipe

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
        for recipe in recipes:
            recipe.recalculate_ingredient_aggregates()