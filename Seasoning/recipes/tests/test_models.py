'''
Created on Jul 6, 2015

@author: joep
'''
from django.test import TestCase
from django_dynamic_fixture import G
from recipes.models import Recipe, UsesIngredient
from ingredients.models import Ingredient, Unit, CanUseUnit

class RecipeModelTest(TestCase):
    
    def test_footprint(self):
        recipe = G(Recipe, portions=2)
        
        ing = G(Ingredient, base_footprint=1, category=Ingredient.BASIC)
        unit = G(Unit, parent_unit=None)
        G(CanUseUnit, ingredient=ing, unit=unit, is_primary_unit=True, conversion_ratio=1)
        
        G(UsesIngredient, recipe=recipe, ingredient=ing, amount=1, unit=unit)
        
        self.assertEqual(recipe.total_footprint(), 1)
        self.assertEqual(recipe.normalized_footprint(), 0.5)



class UsesIngredientModelTest(TestCase):
    
    def test_conversion_ratio(self):
        ing = G(Ingredient)
        unit = G(Unit, parent_unit=None)
        G(CanUseUnit, ingredient=ing, unit=unit, conversion_ratio=0.5)
        
        uses = G(UsesIngredient, ingredient=ing, unit=unit)
        
        self.assertEqual(uses.unit_conversion_ratio(), 0.5)
    
    def test_conversion_ratio_parent_unit(self):
        ing = G(Ingredient)
        punit = G(Unit, parent_unit=None)
        unit = G(Unit, parent_unit=punit, ratio=0.1)
        G(CanUseUnit, ingredient=ing, unit=punit, conversion_ratio=1)
        
        uses = G(UsesIngredient, ingredient=ing, unit=unit)
        
        self.assertEqual(uses.unit_conversion_ratio(), 0.1)
        
    
    def test_footprint(self):
        ing = G(Ingredient, base_footprint=1, category=Ingredient.BASIC)
        unit = G(Unit, parent_unit=None)
        G(CanUseUnit, ingredient=ing, unit=unit, is_primary_unit=True, conversion_ratior=1)
        
        uses = G(UsesIngredient, ingredient=ing, amount=1, unit=unit)
        
        self.assertEqual(uses.footprint(), 1)