from django.core.management.base import NoArgsCommand
from recipes.models import Recipe

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        Recalculate the denormalized aggregate values of all recipes.
        
        """
        for recipe in Recipe.objects.all():
            recipe.recalculate_ingredient_aggregates()