'''
Created on Jul 9, 2015

@author: joep
'''
import requests
import bs4
import re

def get_recipe_categories():
    categories_page = bs4.BeautifulSoup(requests.get('http://smulhuisje.blogspot.be/p/recepten-hartig.html').content)
    
    category_links = categories_page.find('div', class_='post-body').find_all('a', target='_blank')
    
    return {link.text.strip(): link['href'] for link in category_links}

def get_recipe_pages():
    for category_name, category_link in get_recipe_categories().items():
        
        recipes_page = bs4.BeautifulSoup(requests.get(category_link))
        
        while True:
            
            if recipes_page.find('h3', class_='post-title') is None:
                break
            
            for recipe in recipes_page.find_all('h3', class_='post-title'):
                yield RecipePage(url=recipe.find('a')['href'],
                                 category_name=category_name)
            
            recipes_page = bs4.BeautifulSoup(requests.get(recipes_page.find('a', class_='blog-pager-older-link')['href']))

def debug_get_recipe_page(url):
    return RecipePage(url=url,
                      category_name='',
                      description='')
            

class RecipePage(object):
    
    def __init__(self, url, category_name):
        self.url = url
        self._content = None

        self.recipe_course = category_name        
        self.recipe_cuisine = None
        self.recipe_description = None
        
    @property
    def content(self):
        if self._content is None:
            self._content = bs4.BeautifulSoup(requests.get(self.url).content)
        return self._content.find('div', class_='post')
    
    @property
    def recipe_name(self):
        return self.content.find('h3', class_='post-title').text.strip()
    
    @property
    def recipe_portions(self):
        m = re.match('(\d+)\ +personen', self.content.text)
        
        if m:
            return int(m.groups(1))
        
        return None
    
    @property
    def recipe_ingredients(self):
        for ing_el in self.content.find_all('strong'):
            if 'Dit heb je nodig' in ing_el.text:
                continue
            if ing_el.text.strip().startswith('('):
                continue
            
            ing_parts = ing_el.text.strip().split()
                    
            if len(ing_parts) > 2:
                unit = ing_parts[1]
                del ing_parts[1]
            else:
                unit = None
            
            if len(ing_parts) > 1 and re.match('\d+(\/\d+)?', ing_parts[0]):
                amount = ing_parts[0]
                del ing_parts[0]
            else:
                amount = 1
                
            ing_name = ' '.join(ing_parts)
            
            yield ing_name, amount, unit, None
            
    
    @property
    def recipe_image(self):
        return self.content.find('img')['src']
    
    @property
    def recipe_source(self):
        return self.url
    