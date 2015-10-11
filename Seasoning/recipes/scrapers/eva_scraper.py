import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError

def get_recipe_pages():
    page = 1
    
    last_recipe_page_first_recipe_url = None
    while True:
        first = True
        
        resp = requests.post('http://www.evavzw.be/system/ajax',
                              data={'allergy': '_none',
                                      'cooking_time': '_none',
                                      'difficulty': '_none',
                                      'form_build_id': 'form-l6NAU4f0M7qBaROO7AlEI5-un17mswynGfBo7YlYJDE',
                                      'form_id': 'ingredient_search_form',
                                      'ingredient': '',
                                      'page': page,
                                      'region': '_none',
                                      'types': '_none'})
        
        recipes_html = None
        
        if resp.content == '':
            raise HTTPError('Eva Scraper could not retrieve data from evavzw.be')
        
        for result_dict in resp.json():
            if len(result_dict.get('data', '')) > 0:
                recipes_html = BeautifulSoup(result_dict['data'])
                break
            
        if recipes_html is None:
            return None
        
        for recipe_div in recipes_html.find_all(class_='node-recipe'):
            recipe_page = RecipePage(url=recipe_div.find('h3').find('a')['href'],
                                     thumb_url=recipe_div.find('img')['src'])
            
            if first:
                if last_recipe_page_first_recipe_url == recipe_page.url:
                    raise StopIteration()
                
                last_recipe_page_first_recipe_url = recipe_page.url
                first = False
            
            yield recipe_page
                
        page += 1



class RecipePage(object):
    
    def __init__(self, url, thumb_url):
        self.url = 'http://www.evavzw.be{}'.format(url.replace('http://www.evavzw.be', ''))
        self.thumb_url = thumb_url
        self._content = None
        
        self.recipe_description = None
    
    @property
    def content(self):
        if self._content is None:
            self._content = BeautifulSoup(requests.get(self.url).text)
        return self._content
    
    @property
    def recipe_name(self):
        return self.content.find('div', class_='data-wrapper').find('h2').text
    
    @property
    def recipe_portions(self):
        return int(self.content.find('div', class_='ingredients-wrapper').find('h2').text.split()[2])
    
    @property
    def recipe_ingredients(self):
        ing_lis = self.content.find('div', class_='ingredients-wrapper').find_all('li')
        
        for ing_li in ing_lis:
            ing_name = ing_li.find('a').text
            # Delete everything in this element starting at the ingredient name
            parts = ing_li.text[:ing_li.text.find(ing_name)].strip().split()
            
            try:
                if len(parts) > 1 and parts[1] == '-':
                    # The amount has an upper and lower limit 'x - y kg'
                    # Delete the lower limit 
                    del parts[0]
                    # Delete the -
                    del parts[0]
                    
                amount = float(parts[0].replace(',', '.'))
            except (ValueError, IndexError):
                amount = None
            
            try:
                unit = parts[1]    
                if unit == 'g':
                    unit = 'gram'
                if unit.lower() in ['kleine', 'grote', 'dikke', 'biologische', 'middelgrote']:
                    unit = None
            except (IndexError):
                unit = None
                
            if ' & ' in ing_name or ' en ' in ing_name:
                ing_names = ing_name.replace(' & ', ' en ').split(' en ')
                yield ing_names[0].strip(), amount, unit
                ing_name = ing_names[1].strip()
                
            yield ing_name, amount, unit, None
    
    @property
    def recipe_course(self):
        extra_info_lis = self.content.find('div', class_='extra-info-wrapper').find_all('li')
        for li in extra_info_lis:
            if 'Type' in li.text:
                return li.find('a').text
        return None
    
    @property
    def recipe_cuisine(self):
        extra_info_lis = self.content.find('div', class_='extra-info-wrapper').find_all('li')
        for li in extra_info_lis:
            if 'Regio' in li.text:
                return li.find('a').text
        return None
    
    @property
    def recipe_image(self):
        header_img_url = self.content.find('div', class_='image-wrapper').find('img')['src'].split('?')[0]
        
        if 'recept-header.jpg' in header_img_url:
            return self.thumb_url
        
        return header_img_url
    
    @property
    def recipe_source(self):
        return self.url
    