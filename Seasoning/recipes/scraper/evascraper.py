# -*- coding: utf-8 -*-
from recipes.scraper.browse.browser import Browser as raw_browser
from urllib import urlencode
import re
from django.contrib.auth import get_user_model
from recipes.models import ExternalSite, Recipe, Cuisine
import difflib
import tempfile
import requests
from django.core import files

Browser = lambda: raw_browser('www.evavzw.be')

class RecipePage(object):
    
    def __init__(self, preview_li, content=None):
        self.preview_li = preview_li
        self.url = 'http://www.evavzw.be/%s' % preview_li.find('h3').find('a')['href']
        
        self._content = content
    
    @property
    def content(self):
        if self._content is None:
            self._content = Browser().get(self.url)
        return self._content
    
    @property
    def recipe_name(self):
        return self.content.find('div', {'class': 'articleHeader'}).find('h1').text
    
    @property
    def recipe_portions(self):
        return int(self.content.find('div', {'id': 'recepten-ingredients'}).find('h2').find('strong').text)
    
    @property
    def recipe_ingredients(self):
        ing_table = self.content.find('div', {'id': 'recepten-ingredients'}).find('table')
        for ing_tr in ing_table.find('tbody').find_all('tr'):
            tds = ing_tr.find_all('td')
            if re.match('.*\d+.*', tds[0].text):
                amount_text = tds[0].text
                amount_pieces = amount_text.split()
                amount = float(amount_pieces[0])
                if len(amount_pieces) > 1:
                    unit = amount_pieces[1]
                else:
                    unit = 'stuk'
                ing_name = tds[1].text
            else:
                ing_name = tds[0].text
                amount = 1
                if ing_name.lower() in ['peper', 'zout']:
                    unit = 'snuifje'
                else:
                    unit = 'scheut'
                
            yield ing_name, amount, unit
    
    @property
    def recipe_preparation_time(self):
        time_li = self.preview_li.find('li', {'class': 'tijd'})
        if time_li == None:
            return 0
        return int(time_li.text[:-1])
    
    @property
    def recipe_course(self):
        return self.preview_li.find('ul').find_all('li')[0].find('a').text
    
    @property
    def recipe_cuisine(self):
        lis = self.preview_li.find('ul').find_all('li')
        if len(lis) > 1:
            if not 'tijd' in lis[1].get('class', ''):
                return lis[1].find('a').text
        return None
        
    
    @property
    def recipe_image(self):
        return self.content.find('div', {'id': 'recepten-bereiding'}).find('div').find('img')['src']
    
def get_recipe_pages():
    params = {'option': 'com_content',
              'view': 'article',
              'id': 53,
              'Itemid': 396,
              'limitstart': 0}
    
    while True:
        browse_recipes_page = Browser().get('http://www.evavzw.be/index.php?%s' % urlencode(params))
        recipe_lis = browse_recipes_page.find_all('li', {"class" : "ofrecept" })
        if len(recipe_lis) <= 0:
            return
        
        for recipe_li in recipe_lis:
            yield RecipePage(preview_li=recipe_li)
        
        params['limitstart'] += 24

def scrape_recipes():
    # ALL THA RECIPES ARE MINE!!!
    scraper = get_user_model().objects.get(id=1)
    try:
        external_site = ExternalSite.objects.get(name="Eva vzw")
    except ExternalSite.DoesNotExist:
        external_site = ExternalSite(name="Eva vzw", url='http://www.evavzw.be')
        external_site.save()
    
    cuisines = {cuisine.name: cuisine for cuisine in Cuisine.objects.all()}
        
    recipe_pages = get_recipe_pages()
    
    for recipe_page in recipe_pages:
        # Get course
        recipe_course = None
        try:
            best = difflib.get_close_matches(recipe_page.recipe_course, [x[1] for x in Recipe.COURSES], 1, 0.8)[0]
            
            for code, course in Recipe.COURSES:
                if best == course:
                    recipe_course = code
                    break
        except IndexError:
            pass
        
        # Get cuisine
        recipe_cuisine = None
        if recipe_page.recipe_cuisine is not None:
            try:
                best = difflib.get_close_matches(recipe_page.recipe_cuisine, cuisines.keys(), 1, 0.8)[0]
                
                recipe_cuisine = cuisines[best]
            except IndexError:
                pass
        
        # Get Image file
        # Steam the image from the url
        request = requests.get('http://www.evavzw.be%s' % recipe_page.recipe_image, stream=True)
    
        # Was the request OK?
        if request.status_code != requests.codes.ok:
            # Nope, error handling, skip file etc etc etc
            continue
    
        # Get the filename from the url, used for saving later
        file_name = recipe_page.recipe_image.split('/')[-1]
    
        # Create a temporary file
        lf = tempfile.NamedTemporaryFile()
    
        # Read the streamed image in sections
        for block in request.iter_content(1024 * 8):
    
            # If no more file then stop
            if not block:
                break
    
            # Write image block to temporary file
            lf.write(block)
                
        recipe = Recipe(name=recipe_page.recipe_name, author=scraper, external=True, external_site=external_site,
                        external_url=recipe_page.url, course=recipe_course, cuisine=recipe_cuisine,
                        description='Een heerlijk vegetarisch receptje van Eva!',
                        portions=recipe_page.recipe_portions, active_time=recipe_page.recipe_preparation_time,
                        passive_time=0, visible=False, accepted=False)
        recipe.image.save(file_name, files.File(lf))
        
        for ingredient in recipe_page.recipe_ingredients:
            pass
        break
        print('%s - %s - %s - %s - %s - %s' % (recipe_page.recipe_name, recipe_page.recipe_portions,
                                          recipe_page.recipe_preparation_time, recipe_page.recipe_course,
                                          recipe_page.recipe_cuisine, recipe_page.recipe_image))
        for ingredient in recipe_page.recipe_ingredients:
            print('    %s' % str(ingredient))