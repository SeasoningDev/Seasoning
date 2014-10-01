from django.test import TestCase
from django_dynamic_fixture import G
from django.contrib.auth import get_user_model

class RecipeFormsTestCase(TestCase):
    
    def setUp(self):
        self.user = G(get_user_model(), is_active=True)
        self.user.set_password('test')
        self.user.save()
    
    def test_edit_recipe(self):
        location = '/recipes/add/'
        resp = self.client.get(location)
        # Need to be logged in first
        self.assertRedirects(resp, '/profile/login/?next=' + location, 302, 200)
        
        self.client.post('/profile/login/', {'username': self.user.email,
                                             'password': 'test'})
        
        # TODO: rewrite edit recipe and test it
#         resp = self.client.get(location)
#         
#         self.assertTrue('recipe_form' in resp.context)
#         self.assertTrue(resp.context['new_recipe'])
        