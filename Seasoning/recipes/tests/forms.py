from django.test import TestCase
from django_dynamic_fixture import G
from authentication.models import User
from recipes.models import Cuisine

class RecipeFormsTestCase(TestCase):
    
    def test_edit_recipe(self):
        location = '/recipes/add/'
        resp = self.client.get(location)
        # Need to be logged in first
        self.assertRedirects(resp, '/login/?next=' + location, 302, 200)
        
        self.client.post('/login/', {'username': self.user.email,
                                     'password': 'test'})
        resp = self.client.get(location)
        
        self.assertTrue('recipe_form' in resp.context)
        self.assertTrue(resp.context['new_recipe'])
        