from django.test import TestCase
import json

class IngredientsViewsTestCase(TestCase):
    fixtures = ['ingredients.json']
    
    def test_view_ingredient(self):
        resp = self.client.get('/ingredients/100/')
        self.assertEqual(resp.status_code, 404)
        
        resp = self.client.get('/ingredients/1/')
        self.assertEqual(resp.status_code, 200)
        
        self.assertNumQueries(6, lambda: self.client.get('/ingredients/1/'))
        
    def test_ajax_ingredient_name_list(self):
        # get requests shouldn't be answered
        resp = self.client.get('/ingredients/ing_list/a/')
        self.assertEqual(resp.status_code, 404)
        
        # TODO: rewrite with SearchIngredientForm instead of url parameters
#         resp = self.client.post('/ingredients/ing_list/a/', {'HTTP_X_REQUESTED_WITH='XMLHttpRequest')
#         self.assertEqual(resp.status_code, 200)
#         ings = json.loads(resp.content)
#         self.assertEqual(len(ings), 2)
#         self.assertEqual(ings[0][0], 2)
#         self.assertEqual(ings[1][0], 1)
