from django.test import TestCase
from django.core.exceptions import ValidationError
from django_dynamic_fixture import G, N
from ingredients.models import Ingredient, Unit, CanUseUnit
from recipes.models import Recipe, UsesIngredient, Cuisine
from authentication.models import User


class UsesIngredientModelTestCase(TestCase):
    
    def setUp(self):
        G(Cuisine, name='Andere')
        Recipe(name='h', course=1, author=G(User), description='t', portions=1,
               active_time=1, passive_time=1, instructions='a').save()
    
    def test_clean(self):
        cuu = G(CanUseUnit)
        cuu.ingredient.accepted = True
        cuu.ingredient.save()
        unit = G(Unit)
        
        ui = N(UsesIngredient, ingredient=cuu.ingredient, unit=unit)
        self.assertRaises(ValidationError, ui.clean)
        
        ui = N(UsesIngredient, ingredient=cuu.ingredient, unit=cuu.unit)
        self.assertEqual(ui.clean(), ui)
    
    def test_save(self):
        ing = G(Ingredient, type=Ingredient.BASIC, base_footprint=50, accepted=True)
        cuu = G(CanUseUnit, ingredient=ing, conversion_factor=1)
        rec = G(Recipe, portions=1)
        uses = G(UsesIngredient, recipe=rec, ingredient=ing, unit=cuu.unit, amount=1)
        
        self.assertEqual(uses.footprint(), 50)
        self.assertEqual(uses.recipe.footprint, 50)
        
        ing.base_footprint = 5
        ing.save()
        
        uses = UsesIngredient.objects.get(pk=uses.pk)
        self.assertEqual(uses.footprint(), 5)
        self.assertEqual(uses.recipe.footprint, 50)
        
        uses.save()
        self.assertEqual(uses.footprint(), 5)
        self.assertEqual(uses.recipe.footprint, 5)

class RecipeModelTestCase(TestCase):
    
    def setUp(self):
        G(Cuisine, name='Andere')
    
    def test_save(self):
        recipe = G(Recipe, footprint=10, portions=1)
        self.assertEqual(recipe.footprint, 10)
        self.assertEqual(recipe.veganism, Ingredient.VEGAN)
        
        ing = G(Ingredient, type=Ingredient.BASIC, base_footprint=50, veganism=Ingredient.VEGETARIAN, accepted=True)
        cuu = G(CanUseUnit, ingredient=ing, conversion_factor=1)
        G(UsesIngredient, recipe=recipe, ingredient=ing, unit=cuu.unit, amount=1)
        
        self.assertEqual(recipe.footprint, 50)
        self.assertEqual(recipe.veganism, Ingredient.VEGETARIAN)
    
    def test_total_footprint(self):
        recipe = G(Recipe, portions=5)
        self.assertEqual(recipe.total_footprint(), 0)
        
        ing = G(Ingredient, type=Ingredient.BASIC, base_footprint=50, accepted=True)
        cuu = G(CanUseUnit, ingredient=ing, conversion_factor=1)
        G(UsesIngredient, recipe=recipe, ingredient=ing, unit=cuu.unit, amount=1)
        recipe.save()
        self.assertEqual(recipe.total_footprint(), 50)
    
    def test_vote(self):
        recipe = G(Recipe)
        
        self.assertEqual(recipe.upvotes, 0)
        
        recipe.upvote(recipe.author)
        self.assertEqual(recipe.upvotes, 1)
        # Assert double upvotes are not possible
        recipe.upvote(recipe.author)
        self.assertEqual(recipe.upvotes, 1)
        
        recipe.downvote(recipe.author)
        self.assertEqual(recipe.upvotes, 0)
        # Assert double downvotes are not possible
        recipe.downvote(recipe.author)
        self.assertEqual(recipe.upvotes, 0)
        