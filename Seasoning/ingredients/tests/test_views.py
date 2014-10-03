from django.test import TestCase
import json
from django.core.urlresolvers import reverse

class IngredientsStandardViewsTestCase(TestCase):
    fixtures = ['ingredients.json']
    
    def test_view_ingredient(self):
        resp = self.client.get(reverse('view_ingredient', args=[100]))
        self.assertEqual(resp.status_code, 404)
        
        resp = self.client.get(reverse('view_ingredient', args=[1]))
        self.assertEqual(resp.status_code, 200)
        
        self.assertNumQueries(6, lambda: self.client.get(reverse('view_ingredient', args=[1])))



class IngredientsAjaxViewsTestCase(TestCase):
    fixtures = ['ingredients.json']
    
    def test_ajax_ingredient_name_list(self):
        # get and non-ajax requests shouldn't be answered
        resp = self.client.get(reverse('ajax_ingredient_name_list'))
        self.assertEqual(resp.status_code, 403)
        resp = self.client.post(reverse('ajax_ingredient_name_list'))
        self.assertEqual(resp.status_code, 403)
        
        resp = self.client.post(reverse('ajax_ingredient_name_list'),
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 200)
        
        # No query string -> get all ingredients and synonyms
        ings = json.loads(resp.content)
        self.assertEqual(len(ings), 4)
        
        
        resp = self.client.post(reverse('ajax_ingredient_name_list'),
                                {'query': 'a'},
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 200)
        
        ings = json.loads(resp.content)
        self.assertEqual(len(ings), 2)
        for ing in ings:
            self.assertTrue('a' in ing['value'])
    
    def test_ajax_ingredient_list(self):
        # get and non-ajax requests shouldn't be answered
        resp = self.client.get(reverse('ajax_ingredient_list'))
        self.assertEqual(resp.status_code, 403)
        resp = self.client.post(reverse('ajax_ingredient_list'))
        self.assertEqual(resp.status_code, 403)
        
        