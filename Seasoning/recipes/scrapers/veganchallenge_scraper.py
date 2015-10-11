'''
Created on Jul 24, 2015

@author: joep
'''
import requests
import bs4
import re
from recipes.scrapers.ingredient_parser import parse_ingredient_line

def get_recipe_pages():
    page = 1
    
    while True:
        resp = requests.post('http://veganchallenge.nl/getrecipes/',
                              data={'page': page})
        
        recipes_html = bs4.BeautifulSoup(resp.content)

        if recipes_html.find('div', class_='receptitem') is None:
            break
                
        for recipe_div in recipes_html.find_all('div', class_='receptitem'):
            recipe_page = RecipePage(url=recipe_div.find('a')['href'])
            
            yield recipe_page
                
        page += 1
        
        

class RecipePage(object):
    
    def __init__(self, url):
        self.url = url
        self._content = None
        
        self.recipe_description = None
    
    @property
    def content(self):
        if self._content is None:
            self._content = bs4.BeautifulSoup(requests.get(self.url).content).find('section', id='content')
        return self._content
    
    @property
    def recipe_name(self):
        return self.content.find('h1').text
    
    @property
    def recipe_portions(self):
        portions_string = self.content.find('div', class_='recipeinfo').find('div').text
        
        m = re.match('.*(\d+)-Persoons.*', portions_string)
        if not m:
            m = re.match('.*(\d+)\ Personen.*', portions_string)
            if not m:
                raise NotImplementedError('Bad portions string: {}'.format(portions_string))
        
        return m.group(1)
    
    @property
    def recipe_ingredients(self):
        ingredient_lis = self.content.find('h2', text=re.compile('Ingrediënten')).find_parent().find_all('li')
        
        for li in ingredient_lis:
            if li.text.strip() == '':
                continue
            
            if ':' in li.text:
                continue
            
            yield parse_ingredient_line(li.text)
    
    @property
    def recipe_course(self):
        if self.content.find('div', class_='recipeinfo').find('div', text=re.compile('Menugang:')) is not None:
            return self.content.find('div', class_='recipeinfo').find('div', text=re.compile('Menugang:')).find_next_sibling().text.strip()
        
        if self.content.find('div', class_='recipeinfo').find('div', text=re.compile('Type:')) is not None:
            return self.content.find('div', class_='recipeinfo').find('div', text=re.compile('Type:')).find_next_sibling().text.strip()
        
        return None
    
    @property
    def recipe_cuisine(self):
        if self.content.find('div', class_='recipeinfo').find('div', text=re.compile('Keuken:')) is None:
            return None
        
        return self.content.find('div', class_='recipeinfo').find('div', text=re.compile('Keuken:')).find_next_sibling().text.strip()
        
    @property
    def recipe_image(self):
        return self.content.find('div', class_='col_1_2 right recipeimg').find('img')['src']
    
    @property
    def recipe_source(self):
        return self.url