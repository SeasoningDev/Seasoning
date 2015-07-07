'''
Created on Jul 7, 2015

@author: joep
'''
from django.test import TestCase
from django_dynamic_fixture import G
from recipes.models import Recipe
from recipes.forms import RecipeSearchForm

class RecipeSearchFormTest(TestCase):
    
    def setUp(self):
        self.recipe = G(Recipe, name='Test Recipe')
        G(Recipe, name='Bad')
    
    
    
    def test_search_query(self):
        form = RecipeSearchForm({'search_query': ''})
        self.assertEqual(form.search_queryset().count(), 2)
        self.assertIn(self.recipe, form.search_queryset())
        
        form = RecipeSearchForm({'search_query': 'test'})
        self.assertEqual(form.search_queryset().count(), 1)
        self.assertIn(self.recipe, form.search_queryset())
        
        form = RecipeSearchForm({'search_query': 'tester'})
        self.assertEqual(form.search_queryset().count(), 0)
        
    def test_form_nothing(self):
        form = RecipeSearchForm({})
        form.is_valid()
        print(form.errors)
        self.assertTrue(form.is_valid())
        