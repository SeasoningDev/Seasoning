import re, requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from recipes.scrapers.ingredient_parser import parse_ingredient_line

def get_recipe_pages():

    resp = requests.get('http://www.een.be/sites/een.be/modules/custom/recipe/iframes/recepten.php')
     
    if resp.content == '':
        raise HTTPError('Eva Scraper could not retrieve data from evavzw.be')
     
    recipes_html = BeautifulSoup(resp.content, 'html.parser')
     
    if recipes_html is None:
        return None
     
    for recipe_td in recipes_html.find_all('td', class_='recipe'):
        recipe_a = recipe_td.find('a')
        yield RecipePage(url=recipe_a['href'], name=recipe_a.text)
    


class RecipePage(object):
    
    def __init__(self, url, name):
        self.url = 'http://www.een.be{}'.format(url.replace('http://www.een.be', ''))
        self.name = name
        self._content = None
        
    @property
    def content(self):
        if self._content is None:
            self._content = BeautifulSoup(requests.get(self.url).text, 'html.parser')
        return self._content
    
    @property
    def recipe_name(self):
        return self.name

    @property
    def recipe_description(self):
        return None
    
    @property
    def recipe_portions(self):
        return int(self.content.find('a', class_='active', text=re.compile('\d+\ personen')).text.replace('personen', '').strip())
    
    @property
    def recipe_ingredients(self):
        ing_lis = self.content.find('div', class_='recipe-ingredients').find_all('li')
        
        for ing_li in ing_lis:
            yield parse_ingredient_line(ing_li.text.strip())
    
    @property
    def recipe_course(self):
        return None
    
    @property
    def recipe_cuisine(self):
        return None
    
    @property
    def recipe_image(self):
        return self.content.find('meta', property='og:image')['content']
    
    @property
    def recipe_source(self):
        return self.url
    
