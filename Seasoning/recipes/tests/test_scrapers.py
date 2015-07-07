'''
Created on Jul 6, 2015

@author: joep
'''
from django.test import TestCase
from recipes.scrapers.eva_scraper import get_recipe_pages

class EvaScraperTest(TestCase):
    
    def test_get_recipe_pages(self):
        recipe_pages = list(get_recipe_pages(1))
        
        self.assertGreater(len(recipe_pages), 0)
        self.assertIn('/recept', recipe_pages[0].url)
        
    def test_get_recipe_pages_last_page(self):
        recipe_page_1 = list(get_recipe_pages(27))
        
        recipe_page_2 = list(get_recipe_pages(28))
        
        self.assertEqual(recipe_page_1[0].url, recipe_page_2[0].url)