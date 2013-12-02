from django.test import TestCase
from django_dynamic_fixture import G
from authentication.models import User
from recipes.models import Cuisine
from ingredients.models import Ingredient, Unit, CanUseUnit

class RecipeViewsTestCase(TestCase):
    
    def setUp(self):
        self.user = G(User, is_active=True)
        self.user.set_password('test')
        self.user.save()
        self.cuisine = G(Cuisine, name='Andere')
        ing = G(Ingredient, name='Aardappel', accepted=True)
        unit = G(Unit)
        G(CanUseUnit, ingredient=ing, unit=unit)
        ing2 = G(Ingredient, name='Aardbei', accepted=True)
        G(CanUseUnit, ingredient=ing2, unit=unit)
        
    
#    def test_view_recipe(self):
#        resp = self.client.get('/recipes/1/')
#        self.assertEqual(resp.status_code, 200)
#        
#        self.assertNumQueries(4, lambda: self.client.get('/recipes/1/'))
    
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
    
    def test_add_recipe_one_ingredient(self):
        location = '/recipes/add/'
        self.client.post('/login/', {'username': self.user.email,
                                     'password': 'test'})
        self.client.get(location)
        
        useable_unit = Ingredient.objects.get(name='Aardappel').useable_units.all()[0]
        
        # Add recipe with 1 ingredient
        post_dict = {u'uses-TOTAL_FORMS': [u'1'], u'uses-INITIAL_FORMS': [u'0'], u'uses-MAX_NUM_FORMS': [u'1000'], 
                     u'uses-0-id': [u''], u'uses-0-ingredient': [u'Aardappel'], u'uses-0-amount': [u'1'], u'uses-0-unit': [unicode(useable_unit.id)], u'uses-0-group': [u''], u'uses-0-DELETE': [u''],
                     
                     u'uses-__prefix__-id': [u''], u'uses-__prefix__-ingredient': [u''], u'uses-__prefix__-amount': [u''], u'uses-__prefix__-unit': [u''], u'uses-__prefix__-group': [u''], 
                     u'normal-submit': [u'Toevoegen'], 
                     u'image': [u''], u'extra_info': [u''], u'cuisine': [unicode(self.cuisine.id)], u'description': [u'a'], u'passive_time': [u'1'], u'instructions': [u'a'], u'initial-cuisine': [u'13'], 
                     u'portions': [u'1'], u'name': [u'test'], u'course': [u'0'], u'active_time': [u'1'],
                     u'csrfmiddlewaretoken': [u'6DjLoeb2BC6FCL3O53355Sdv4KKYrpZv']}
        resp = self.client.post(location, post_dict, follow=True)
        
        self.assertTrue('recipe' in resp.context)
        new_recipe = resp.context['recipe']
        self.assertRedirects(resp, '/recipes/%d/' % new_recipe.id, 302, 200)
        self.assertEquals(len(new_recipe.uses.all()), 1)
        uses = new_recipe.uses.all()[0]
        self.assertEqual(uses.group, '')
    
    def test_add_recipe_two_ingredients(self):
        location = '/recipes/add/'
        self.client.post('/login/', {'username': self.user.email,
                                     'password': 'test'})
        self.client.get(location)
        
        useable_unit = Ingredient.objects.get(name='Aardappel').useable_units.all()[0]
        
        # Add recipe with 2 ingredients
        post_dict = {u'uses-TOTAL_FORMS': [u'2'], u'uses-INITIAL_FORMS': [u'0'], u'uses-MAX_NUM_FORMS': [u'1000'], 
                     u'uses-0-id': [u''], u'uses-0-ingredient': [u'Aardappel'], u'uses-0-amount': [u'1'], u'uses-0-unit': [unicode(useable_unit.id)], u'uses-0-group': [u''], u'uses-0-DELETE': [u''], 
                     u'uses-1-id': [u''], u'uses-1-ingredient': [u'Aardbei'], u'uses-1-amount': [u'1'], u'uses-1-unit': [unicode(useable_unit.id)], u'uses-1-group': [u''], 
                     
                     u'uses-__prefix__-id': [u''], u'uses-__prefix__-ingredient': [u''], u'uses-__prefix__-amount': [u''], u'uses-__prefix__-unit': [u''], u'uses-__prefix__-group': [u''], 
                     u'normal-submit': [u'Toevoegen'], 
                     u'image': [u''], u'extra_info': [u''], u'cuisine': [unicode(self.cuisine.id)], u'description': [u'a'], u'passive_time': [u'1'], u'instructions': [u'a'], u'initial-cuisine': [u'13'], 
                     u'portions': [u'1'], u'name': [u'test'], u'course': [u'0'], u'active_time': [u'1'],
                     u'csrfmiddlewaretoken': [u'6DjLoeb2BC6FCL3O53355Sdv4KKYrpZv']}
        resp = self.client.post(location, post_dict, follow=True)
        
        self.assertTrue('recipe' in resp.context)
        new_recipe = resp.context['recipe']
        self.assertRedirects(resp, '/recipes/%d/' % new_recipe.id, 302, 200)
        self.assertEquals(len(new_recipe.uses.all()), 2)
        uses = new_recipe.uses.all()
        self.assertEqual(uses[0].group, '')
        self.assertEqual(uses[1].group, '')
        
        # Add recipe with 2 ingredients out of order
        post_dict = {u'uses-TOTAL_FORMS': [u'3'], u'uses-INITIAL_FORMS': [u'0'], u'uses-MAX_NUM_FORMS': [u'1000'], 
                     u'uses-0-id': [u''], u'uses-0-ingredient': [u'Aardappel'], u'uses-0-amount': [u'1'], u'uses-0-unit': [unicode(useable_unit.id)], u'uses-0-group': [u''], u'uses-0-DELETE': [u''], 
                     u'uses-2-id': [u''], u'uses-2-ingredient': [u'Aardbei'], u'uses-2-amount': [u'1'], u'uses-2-unit': [unicode(useable_unit.id)], u'uses-2-group': [u''], 
                     
                     u'uses-__prefix__-id': [u''], u'uses-__prefix__-ingredient': [u''], u'uses-__prefix__-amount': [u''], u'uses-__prefix__-unit': [u''], u'uses-__prefix__-group': [u''], 
                     u'normal-submit': [u'Toevoegen'], 
                     u'image': [u''], u'extra_info': [u''], u'cuisine': [unicode(self.cuisine.id)], u'description': [u'a'], u'passive_time': [u'1'], u'instructions': [u'a'], u'initial-cuisine': [u'13'], 
                     u'portions': [u'1'], u'name': [u'test'], u'course': [u'0'], u'active_time': [u'1'],
                     u'csrfmiddlewaretoken': [u'6DjLoeb2BC6FCL3O53355Sdv4KKYrpZv']}
        resp = self.client.post(location, post_dict, follow=True)
        
        self.assertTrue('recipe' in resp.context)
        new_recipe = resp.context['recipe']
        self.assertRedirects(resp, '/recipes/%d/' % new_recipe.id, 302, 200)
        self.assertEquals(len(new_recipe.uses.all()), 2)
        uses = new_recipe.uses.all()
        self.assertEqual(uses[0].group, '')
        self.assertEqual(uses[1].group, '')
        
    def test_add_recipe_empty_ingredient_with_group(self):
        location = '/recipes/add/'
        self.client.post('/login/', {'username': self.user.email,
                                     'password': 'test'})
        self.client.get(location)
        
        useable_unit = Ingredient.objects.get(name='Aardappel').useable_units.all()[0]
        
        # Add recipe with 1 empty ingredient, with only the group filled in. The empty ingredient should not be validated, and therefor
        # will not prevent the form from being saved 
        post_dict = {u'uses-TOTAL_FORMS': [u'3'], u'uses-INITIAL_FORMS': [u'0'], u'uses-MAX_NUM_FORMS': [u'1000'], 
                     u'uses-0-id': [u''], u'uses-0-ingredient': [u'Aardappel'], u'uses-0-amount': [u'1'], u'uses-0-unit': [unicode(useable_unit.id)], u'uses-0-group': [u''], u'uses-0-DELETE': [u''], 
                     u'uses-1-id': [u''], u'uses-1-ingredient': [u''], u'uses-1-amount': [u''], u'uses-1-unit': [u''], u'uses-1-group': [u''], 
                     u'uses-2-id': [u''], u'uses-2-ingredient': [u''], u'uses-2-amount': [u''], u'uses-2-unit': [u''], u'uses-2-group': [u'test'], 
                     
                     u'uses-__prefix__-id': [u''], u'uses-__prefix__-ingredient': [u''], u'uses-__prefix__-amount': [u''], u'uses-__prefix__-unit': [u''], u'uses-__prefix__-group': [u''], 
                     u'normal-submit': [u'Toevoegen'], 
                     u'image': [u''], u'extra_info': [u''], u'cuisine': [unicode(self.cuisine.id)], u'description': [u'a'], u'passive_time': [u'1'], u'instructions': [u'a'], u'initial-cuisine': [u'13'], 
                     u'portions': [u'1'], u'name': [u'test'], u'course': [u'0'], u'active_time': [u'1'],
                     u'csrfmiddlewaretoken': [u'6DjLoeb2BC6FCL3O53355Sdv4KKYrpZv']}
        
        resp = self.client.post(location, post_dict, follow=True)
        
        self.assertTrue('recipe' in resp.context)
        new_recipe = resp.context['recipe']
        self.assertRedirects(resp, '/recipes/%d/' % new_recipe.id, 302, 200)
        
        