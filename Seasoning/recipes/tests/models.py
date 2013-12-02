from django.test import TestCase
from recipes.models import Recipe, Vote, UsesIngredient, Cuisine
from authentication.models import User
from django.db.utils import IntegrityError
from ingredients.models import Ingredient, Unit, CanUseUnit
from django.core.exceptions import ValidationError
from django_dynamic_fixture import G, N
import time
from django.conf import settings
from django.utils.unittest.case import skipIf, skip
from general.decorators import mysqldb_required

class CuisineModelTestCase(TestCase):
    pass

class VoteModelTestCase(TestCase):
    
    def setUp(self):
        G(Cuisine, name='Andere')
    
    def test_save(self):
        vote = N(Vote)
        self.assertEqual(vote.recipe.rating, None)
        
        old_time_changed = vote.time_changed
        time.sleep(1)
        vote.save()
        self.assertTrue(old_time_changed < vote.time_changed)
        self.assertEqual(vote.recipe.rating, vote.score)
    
    def test_delete(self):
        vote = G(Vote)
        self.assertEqual(vote.recipe.rating, vote.score)
        vote.delete()
        self.assertEqual(vote.recipe.rating, None)
    
class UnkownIngredientModelTestCase(TestCase):
    pass

class UsesIngredientModelTestCase(TestCase):
    
    def setUp(self):
        G(Cuisine, name='Andere')
    
    @mysqldb_required
    def test_clean(self):
        cuu = G(CanUseUnit)
        cuu.ingredient.accepted = True
        cuu.ingredient.save()
        unit = G(Unit)
        
        ui = N(UsesIngredient, ingredient=cuu.ingredient, unit=unit)
        self.assertRaises(ValidationError, ui.clean)
        
        ui = N(UsesIngredient, ingredient=cuu.ingredient, unit=cuu.unit)
        self.assertEqual(ui.clean(), ui)
    
    @mysqldb_required
    def test_save(self):
        ing = G(Ingredient, type=Ingredient.BASIC, base_footprint=50, accepted=True)
        cuu = G(CanUseUnit, ingredient=ing, conversion_factor=1)
        rec = G(Recipe, portions=1)
        uses = G(UsesIngredient, recipe=rec, ingredient=ing, unit=cuu.unit, amount=1)
        
        self.assertEqual(uses.footprint, 50)
        self.assertEqual(uses.recipe.footprint, 50)
        
        ing.base_footprint = 5
        ing.save()
        uses.save()
        
        self.assertEqual(uses.footprint, 5)
        self.assertEqual(uses.recipe.footprint, 5)

class RecipeModelTestCase(TestCase):
    
    def setUp(self):
        G(Cuisine, name='Andere')
    
    @mysqldb_required
    def test_save(self):
        recipe = G(Recipe, footprint=10, portions=1)
        self.assertEqual(recipe.footprint, 0)
        self.assertEqual(recipe.veganism, Ingredient.VEGAN)
        
        ing = G(Ingredient, type=Ingredient.BASIC, base_footprint=50, veganism=Ingredient.VEGETARIAN, accepted=True)
        cuu = G(CanUseUnit, ingredient=ing, conversion_factor=1)
        G(UsesIngredient, recipe=recipe, ingredient=ing, unit=cuu.unit, amount=1)
        recipe.save()
        
        self.assertEqual(recipe.footprint, 50)
        self.assertEqual(recipe.veganism, Ingredient.VEGETARIAN)
    
    @mysqldb_required
    def test_total_footprint(self):
        recipe = G(Recipe, portions=5)
        self.assertEqual(recipe.total_footprint(), 0)
        
        ing = G(Ingredient, type=Ingredient.BASIC, base_footprint=50, accepted=True)
        cuu = G(CanUseUnit, ingredient=ing, conversion_factor=1)
        G(UsesIngredient, recipe=recipe, ingredient=ing, unit=cuu.unit, amount=1)
        recipe.save()
        self.assertEqual(recipe.total_footprint(), 50)
    
    @mysqldb_required
    def test_vote(self):
        recipe = G(Recipe)
        
        self.assertRaises(Vote.DoesNotExist, lambda: Vote.objects.get(recipe=recipe, user=recipe.author))
        recipe.vote(recipe.author, 5)
        
        vote = Vote.objects.get(recipe=recipe, user=recipe.author)
        self.assertEqual(vote.score, 5)
        self.assertEqual(recipe.rating, 5)
        
        recipe.vote(recipe.author, 3)
        vote = Vote.objects.get(recipe=recipe, user=recipe.author)
        self.assertEqual(vote.score, 3)
        self.assertEqual(recipe.rating, 3)
        
        
    
    @mysqldb_required
    def test_unvote(self):
        recipe = G(Recipe)
        recipe.vote(recipe.author, 5)
        recipe.unvote(recipe.author)
        self.assertRaises(Vote.DoesNotExist, lambda: Vote.objects.get(recipe=recipe, user=recipe.author))
    
    @mysqldb_required
    def test_calculate_and_set_rating(self):
        recipe = G(Recipe)
        G(Vote, score=2)
        G(Vote, score=4)
        
        self.assertEqual(recipe.rating, None)
        recipe.calculate_and_set_rating()
        self.assertEqual(recipe.rating, 3)

#class RecipeModelsTestCase(TestCase):
#    fixtures = ['users.json', 'ingredients.json', 'recipes.json', ]
#    
#    def test_vote(self):
#        recipe = Recipe.objects.get(pk=1)
#        user1 = User.objects.get(pk=1)
#        user2 = User.objects.get(pk=2)
#        
#        # New votes must be added correctly
#        vote1 = Vote(user=user1, recipe=recipe, score=5)
#        vote1.save()
#        self.assertEqual(len(recipe.votes.all()), 1)
#        self.assertEqual(recipe.rating, 5)
#        
#        # New votes must trigger rating recalculation
#        Vote(user=user2, recipe=recipe, score=4).save()
#        self.assertEqual(len(recipe.votes.all()), 2)
#        self.assertEqual(recipe.rating, (4 + 5)/2.0)
#        
#        # Deleted votes must trigger rating recalculation
#        vote1.delete()
#        self.assertEqual(len(recipe.votes.all()), 1)
#        self.assertEqual(recipe.rating, 4)
#        
#        # A user cannot vote twice on the same recipe
#        self.assertRaises(IntegrityError, Vote(user=user2, recipe=recipe, score=4).save)
#    
#    def test_uses_ingredient(self):
#        recipe = Recipe.objects.get(pk=1)
#        ing = Ingredient.objects.get(pk=2)
#        unit = Unit.objects.get(pk=1)
#        
#        # Can only use useable units
#        usesing = UsesIngredient(recipe=recipe, ingredient=ing, amount=10, unit=unit)
#        self.assertRaises(ValidationError, usesing.save)
#        
#        # Footprint is calculated correctly
#        unit2 = Unit.objects.get(pk=3)
#        usesing.unit = unit2
#        usesing.save()
#        self.assertEqual(usesing.footprint(), 5)
#        
#        # Unit conversion ratio is applied correctly
#        # 1 this_unit = 0.5 primary_unit
#        CanUseUnit(ingredient=ing, unit=unit, conversion_factor=0.5, is_primary_unit=False).save()
#        usesing = UsesIngredient(recipe=recipe, ingredient=ing, amount=10, unit=unit)
#        usesing.save()
#        self.assertEqual(usesing.footprint(), 2.5)
#    
#    def test_recipe(self):
#        recipe = Recipe.objects.get(pk=1)
#        
#        # Check recipe with no ingredients
#        recipe.save()
#        self.assertEqual(recipe.footprint, 0)
#        self.assertEqual(recipe.veganism, Ingredient.VEGAN)
#        
#        # Check recipe with one Vegetarian ingredient
#        ing = Ingredient.objects.get(pk=2)
#        unit = Unit.objects.get(pk=3)
#        UsesIngredient(recipe=recipe, ingredient=ing, amount=10, unit=unit).save()
#        recipe.save()
#        self.assertEqual(recipe.footprint, 5)
#        self.assertEqual(recipe.veganism, Ingredient.VEGETARIAN)
#        
#        # Check recipe with Vegetarian and non-vegetarian ingredient
#        ing.pk = 3
#        ing.name = ing.name + '2'
#        ing.veganism = Ingredient.NON_VEGETARIAN
#        ing.base_footprint = 2
#        ing.save()
#        CanUseUnit(ingredient=ing, unit=unit, conversion_factor=1, is_primary_unit=True).save()
#        UsesIngredient(recipe=recipe, ingredient=ing, amount=10, unit=unit).save()
#        recipe.save()
#        self.assertEqual(recipe.footprint, 25)
#        self.assertEqual(recipe.veganism, Ingredient.NON_VEGETARIAN)