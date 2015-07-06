'''
Created on Jul 5, 2015

@author: joep
'''
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
import json
from django_dynamic_fixture import G
from recipes.models import Recipe

class GetRecipesViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        
    
    
    def test_get_recipes(self):
        resp = self.client.get(reverse('get_recipes'))
        
        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(str(resp.content, encoding=('utf-8)')))
        self.assertIn('result', json_data)
        self.assertEqual(json_data['result'], '')
        
        G(Recipe)
        resp = self.client.get(reverse('get_recipes'))
        
        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(str(resp.content, encoding=('utf-8)')))
        self.assertIn('result', json_data)
        self.assertNotEqual(len(json_data['result']), '')
    
    def test_get_recipes_results_per_page(self):
        G(Recipe)
        G(Recipe)
        
        resp = self.client.get(reverse('get_recipes'))
        json_data_1 = json.loads(str(resp.content, encoding=('utf-8)')))
        
        resp = self.client.get(reverse('get_recipes_max', args=(1,)))
        json_data = json.loads(str(resp.content, encoding=('utf-8)')))
        
        self.assertLess(len(json_data['result']), len(json_data_1['result']))
        
        