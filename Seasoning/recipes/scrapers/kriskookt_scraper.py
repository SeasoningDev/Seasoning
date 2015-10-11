'''
Created on Jul 9, 2015

@author: joep
'''
import requests
import bs4
import re

def get_recipe_categories():
    home = bs4.BeautifulSoup(requests.get('http://www.kriskookt.be/').content)
    
    category_select = home.find('li', id=re.compile("categories-\d+"))
    
    return {option.text.strip(): option['value'] for option in category_select.find_all('option')}

def get_recipe_pages():
    categories = get_recipe_categories()
    
    for category_name, category_value in categories.items():
        category_page = bs4.BeautifulSoup(requests.get('http://www.kriskookt.be/',
                                                       {'cat': category_value}).content)
        
        recipe_divs = category_page.find_all('div', class_="page-content")
        
        for recipe_div in recipe_divs:
            yield RecipePage(url=recipe_div.find('h3').find('a')['href'],
                             category_name=category_name,
                             description=recipe_div.find('p').text)

def debug_get_recipe_page(url):
    return RecipePage(url=url,
                      category_name='',
                      description='')
            

class RecipePage(object):
    
    def __init__(self, url, category_name, description):
        self.url = url
        self.description = description
        self._content = None

        self.recipe_course = category_name        
        self.recipe_cuisine = None
        self.recipe_description = description
        
    @property
    def content(self):
        if self._content is None:
            self._content = bs4.BeautifulSoup(requests.get(self.url).content)
        return self._content.find('div', class_='post')
    
    @property
    def recipe_name(self):
        return self.content.find('div', class_='entry_header').find('h1').text.strip()
    
    @property
    def recipe_portions(self):
        m = re.match('(\d+)\ +personen', self.content.text)
        
        if m:
            return int(m.groups(1))
        
        return None
    
    @property
    def recipe_ingredients(self):
        ing_start = self.content.find('p', text=re.compile('^\ *[Nn]odig[:]?'))
        if ing_start is None:
            ing_start = self.content.find('strong', text=re.compile('^\ *[Ii]ngrediënten'))
            
            if ing_start is None:
                ing_start = self.content.find('ul')
                if ing_start is not None:
                    ing_start = ing_start.find_previous_sibling()
            else:
                ing_start = ing_start.find_parent()
            
        if ing_start is None:
            raise NotImplementedError('No ingredients found: {}\n{}'.format(self.url, self.content.prettify()))
        
        cur_el = ing_start
        cur_group = None
        while True:
            cur_el = cur_el.find_next_sibling()
            if cur_el is None:
                break
            
            if cur_el.name == 'p':
                if 'tip' in cur_el.text.lower():
                    continue
                if 'werkwijze' in cur_el.text.lower():
                    break
                
                cur_group = cur_el.text.replace(':', '').strip()
                
            elif cur_el.name == 'ul':
                for ing_li in cur_el.find_all('li'):
                    if ing_li.find('p') is not None:
                        ing_li.find('p').clear()
                        
                    ing_parts = ing_li.text.strip().split()
                    
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
                    
            else:
                break
    
    @property
    def recipe_image(self):
        return self.content.find('img')['src']
    
    @property
    def recipe_source(self):
        return self.url
    