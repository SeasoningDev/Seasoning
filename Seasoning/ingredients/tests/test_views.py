from django.test import TestCase
import json
from django.core.urlresolvers import reverse
from django_dynamic_fixture import G
from ingredients.models import Ingredient, Synonym

class GetIngredientNameListViewTestCase(TestCase):
    
    def setUp(self):
        ing = G(Ingredient, name='test', accepted=True)
        G(Ingredient, name='test1', accepted=True)
        G(Ingredient, name='test2', accepted=True)
        G(Synonym, ingredient=ing, name='syn')
        
    
    def test_get_ingredient_name_list(self):
        # get and non-ajax requests shouldn't be answered
        resp = self.client.get(reverse('get_ingredient_name_list'))
        self.assertEqual(resp.status_code, 200)
        
        # No query string -> get all ingredients and synonyms
        ings = json.loads(resp.content.decode('utf-8'))
        self.assertEqual(len(ings), 4)
        
        
        resp = self.client.get(reverse('get_ingredient_name_list'),
                                {'term': 'test'})
        self.assertEqual(resp.status_code, 200)
        
        ings = json.loads(resp.content.decode('utf-8'))
        self.assertEqual(len(ings), 3)
        for ing in ings:
            self.assertTrue('test' in ing['label'])
        
        