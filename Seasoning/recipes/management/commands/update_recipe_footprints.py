from django.core.management.base import BaseCommand
from recipes.models import Recipe, UsesIngredient
from ingredients.models import Ingredient

class Command(BaseCommand):
    def handle(self):
        """
        Recalculate the footprint of all usesingredients that use a seasonal ingredient. Then
        recalculate the footprint of every recipe.
        
        """
        for uses_ingredient in UsesIngredient.objects.filter(ingredient__type__in=[Ingredient.SEASONAL, Ingredient.SEASONAL_SEA]):
            uses_ingredient.save()
            
        for recipe in Recipe.objects.all():
            recipe.save()