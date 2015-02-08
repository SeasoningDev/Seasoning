# -*- coding: utf-8 -*-
from urllib import urlencode
import re
from django.contrib.auth import get_user_model
from recipes.models import ExternalSite, Recipe, Cuisine
import difflib
import tempfile
import requests
from django.core import files
from ingredients.models import Ingredient
from ingredients.models.units import Unit
from recipes.models.t_recipe import IncompleteRecipe, TemporaryIngredient,\
    TemporaryUnit, TemporaryUsesIngredient
from recipes.models.recipe import RecipeImage
import json
import bs4

class RecipePage(object):
    
    def __init__(self, url):
        self.url = 'http://www.evavzw.be%s' % url
        self._content = None
    
    @property
    def content(self):
        if self._content is None:
            self._content = bs4.BeautifulSoup(requests.get(self.url).text)
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
            parts = ing_li.text.split()
            ing_name = ing_li.find('a').text
            
            try:
                amount = float(parts[0].replace(',', '.'))
                unit = parts[1]
            except (ValueError, IndexError):
                amount = None
                unit = None
                
            yield ing_name, amount, unit
    
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
        return self.content.find('div', class_='image-wrapper').find('img')['src'].split('?')[0]
    
    @property
    def recipe_source(self):
        return self.url
    
def get_recipe_pages():
    page = 1
    
    while True:
        params = {'allergy': '_none',
                  'cooking_time': '_none',
                  'difficulty': '_none',
                  'form_build_id': 'form-GgrLYpqd6cXHsBcwTdM0ixxYAcgyJWxXQ4bWGx_k_XQ',
                  'form_id': 'ingredient_search_form',
                  'ingredient': '',    
                  'page': page}
        
#         response = requests.post('http://www.evavzw.be/system/ajax', data=params)
#         print(response.text)
#         
#         json_resp = json.loads(response.text)
#         html_resp = bs4.BeautifulSoup(json_resp[1]['data'])
        
        response = requests.get('http://www.evavzw.be/recepten/')
        html_resp = bs4.BeautifulSoup(response.text)
        
        last_page = int(html_resp.find('li', class_='pager-last').find('a')['href'].split('page=')[-1])
        
        for recipe in html_resp.find_all('div', class_='field-name-title'):
            yield RecipePage(url=recipe.find('a')['href'])
        
        page += 1
        if page > last_page:
            break
    
    return

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
        # If the recipe has already been scraped, skip it
        try:
            IncompleteRecipe.objects.get(name=recipe_page.recipe_name, author=scraper, external_site=external_site)
            continue
        except IncompleteRecipe.DoesNotExist:
            try:
                Recipe.objects.get(name=recipe_page.recipe_name, author=scraper, external_site=external_site)
                continue
            except Recipe.DoesNotExist:
                pass
        
        # Get course
        recipe_course = None
        try:
            if recipe_page.recipe_course is not None:
                best = difflib.get_close_matches(recipe_page.recipe_course, [x[1] for x in Recipe.COURSES], 1, 0.8)[0]
                
                for code, course in Recipe.COURSES:
                    if best == course:
                        recipe_course = code
                        break
        except IndexError:
            pass
        
        # Get cuisine
        recipe_cuisine = None
        recipe_cuisine_proposal = None
        if recipe_page.recipe_cuisine is not None:
            try:
                best = difflib.get_close_matches(recipe_page.recipe_cuisine, cuisines.keys(), 1, 0.8)[0]
                
                recipe_cuisine = cuisines[best]
            except IndexError:
                recipe_cuisine_proposal = recipe_page.recipe_cuisine
        
        # Get Image file
        # Steam the image from the url
        request = requests.get(recipe_page.recipe_image, stream=True)
    
        # Was the request OK?
        if request.status_code != requests.codes['ok']:
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
        
        recipe = IncompleteRecipe(name=recipe_page.recipe_name, author=scraper,
                                  external=True, external_site=external_site, external_url=recipe_page.url, 
                                  course=recipe_course, cuisine=recipe_cuisine, cuisine_proposal=recipe_cuisine_proposal,
                                  portions=recipe_page.recipe_portions, active_time=0,
                                  passive_time=0)
        
        if recipe.course is None:
            recipe.course = 0
            recipe.instructions = 'Course: %s\n' % recipe_page.recipe_course
        
        if recipe_page.recipe_source is not None:
            if recipe.instructions is None:
                recipe.instructions = ''
            recipe.instructions += 'Source: %s\n' % recipe_page.recipe_source.strip()
        
        recipe.save()
        
        image = RecipeImage(incomplete_recipe=recipe, added_by=scraper)
        image.image.save(file_name, files.File(lf))
        
        for recipe_ingredient in recipe_page.recipe_ingredients:
            parsed_ing_name = recipe_ingredient[0]
            parsed_amount = recipe_ingredient[1]
            parsed_unit_name = recipe_ingredient[2]
            
            try:
                ingredient = Ingredient.objects.filter(name__icontains=parsed_ing_name)[0]
            except IndexError:
                ingredient = None
            
            if parsed_unit_name is None:
                unit = Unit.objects.get(name__icontains='snuifje')
                parsed_amount = 1
                parsed_unit_name = 'snuifje'
            else:
                try:
                    unit = Unit.objects.filter(short_name__icontains=parsed_unit_name)[0]
                except (ValueError, IndexError):
                    unit = None
            
            t_ingredient = TemporaryIngredient(ingredient=ingredient, name=parsed_ing_name)
            t_ingredient.save()
            
            t_unit = TemporaryUnit(unit=unit, name=parsed_unit_name)
            t_unit.save()
            
            t_uses = TemporaryUsesIngredient(recipe=recipe, ingredient=t_ingredient, amount=parsed_amount,
                                             unit=t_unit)
            t_uses.save()