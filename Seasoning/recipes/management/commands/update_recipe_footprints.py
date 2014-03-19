from django.core.management.base import NoArgsCommand
from ingredients.models import Ingredient
from recipes.models import Recipe, UsesIngredient

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        Recalculate the footprint of all usesingredients that use a seasonal ingredient. Then
        recalculate the footprint of every recipe.
        
        """
        for uses_ingredient in UsesIngredient.objects.filter(ingredient__type__in=[Ingredient.SEASONAL, Ingredient.SEASONAL_SEA]):
            print uses_ingredient
            uses_ingredient.save()
            
        for recipe in Recipe.objects.all():
            print recipe
            recipe.save()