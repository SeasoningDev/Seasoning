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
from django.db import models

class RecipePage(object):
    
    def __init__(self, url):
        self.url = 'http://www.evavzw.be{}'.format(url.replace('http://www.evavzw.be', ''))
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
    
def get_recipe_pages(url=None):
    if url is not None:
        yield RecipePage(url)
        return
    
    page = 1
    recipes = 0
    
    while True:
        params =   {'_triggering_element_name': 'op',
                    '_triggering_element_value': 'submit',
                    'ajax_html_ids%5B%5D': 'wrapper',
                    'ajax_html_ids%5B%5D': 'header',
                    'ajax_html_ids%5B%5D': 'header-inner',
                    'ajax_html_ids%5B%5D': 'block-global-header-menu',
                    'ajax_html_ids%5B%5D': 'block-search-form',
                    'ajax_html_ids%5B%5D': 'search-block-form',
                    'ajax_html_ids%5B%5D': 'edit-search-block-form--2',
                    'ajax_html_ids%5B%5D': 'edit-actions',
                    'ajax_html_ids%5B%5D': 'edit-submit--2',
                    'ajax_html_ids%5B%5D': 'block-global-header-lid',
                    'ajax_html_ids%5B%5D': 'logo_canvas_link',
                    'ajax_html_ids%5B%5D': 'logo_canvas',
                    'ajax_html_ids%5B%5D': 'navigation',
                    'ajax_html_ids%5B%5D': 'block-global-global-main-menu',
                    'ajax_html_ids%5B%5D': 'mobile_nav_btns',
                    'ajax_html_ids%5B%5D': 'main',
                    'ajax_html_ids%5B%5D': 'main-inner',
                    'ajax_html_ids%5B%5D': 'content',
                    'ajax_html_ids%5B%5D': 'content-inner',
                    'ajax_html_ids%5B%5D': 'breadcrumb',
                    'ajax_html_ids%5B%5D': 'main-content',
                    'ajax_html_ids%5B%5D': 'title',
                    'ajax_html_ids%5B%5D': 'page-title',
                    'ajax_html_ids%5B%5D': 'block-system-main',
                    'ajax_html_ids%5B%5D': 'ingredient-search-form',
                    'ajax_html_ids%5B%5D': 'edit-ingredient',
                    'ajax_html_ids%5B%5D': 'edit-ingredient-autocomplete',
                    'ajax_html_ids%5B%5D': 'edit-ingredient-autocomplete-aria-live',
                    'ajax_html_ids%5B%5D': 'edit-types',
                    'ajax_html_ids%5B%5D': 'edit-cooking-time',
                    'ajax_html_ids%5B%5D': 'edit-difficulty',
                    'ajax_html_ids%5B%5D': 'edit-allergy',
                    'ajax_html_ids%5B%5D': 'edit-region',
                    'ajax_html_ids%5B%5D': 'edit-submit',
                    'ajax_html_ids%5B%5D': 'ajax-form-replace-wrapper',
                    'ajax_html_ids%5B%5D': 'block-global-content-information-footer',
                    'ajax_html_ids%5B%5D': 'global-remarks-form',
                    'ajax_html_ids%5B%5D': 'ajax-wrapper',
                    'ajax_html_ids%5B%5D': 'edit-name',
                    'ajax_html_ids%5B%5D': 'edit-mail',
                    'ajax_html_ids%5B%5D': 'edit-remark',
                    'ajax_html_ids%5B%5D': 'edit-submit--3',
                    'ajax_html_ids%5B%5D': 'block-global-newsletter',
                    'ajax_html_ids%5B%5D': 'global-newsletter-form',
                    'ajax_html_ids%5B%5D': 'edit-container',
                    'ajax_html_ids%5B%5D': 'edit-email',
                    'ajax_html_ids%5B%5D': 'edit-submit--2',
                    'ajax_html_ids%5B%5D': 'block-global-action-menu',
                    'ajax_html_ids%5B%5D': 'mobile_nav',
                    'ajax_html_ids%5B%5D': 'search-block-form',
                    'ajax_html_ids%5B%5D': 'edit-search-block-form--2',
                    'ajax_html_ids%5B%5D': 'edit-actions',
                    'ajax_html_ids%5B%5D': 'edit-submit--2',
                    'ajax_html_ids%5B%5D': 'footer',
                    'ajax_html_ids%5B%5D': 'footer-inner',
                    'ajax_html_ids%5B%5D': 'block-global-footer-sitemap',
                    'ajax_html_ids%5B%5D': 'block-global-footer',
                    'ajax_html_ids%5B%5D': 'closure',
                    'ajax_html_ids%5B%5D': 'closure-inner',
                    'ajax_html_ids%5B%5D': '_atssh',
                    'ajax_html_ids%5B%5D': '_atssh618',
                    'ajax_page_state%5Bcss%5D%5Bmodules%2Ffield%2Ftheme%2Ffield.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bmodules%2Fnode%2Fnode.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bmodules%2Fsearch%2Fsearch.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bmodules%2Fsystem%2Fsystem.base.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bmodules%2Fsystem%2Fsystem.menus.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bmodules%2Fsystem%2Fsystem.messages.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bmodules%2Fsystem%2Fsystem.theme.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bmodules%2Fuser%2Fuser.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bprofiles%2Fwieni%2Fthemes%2Fwienibase%2Fcss%2Fbase.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fcontrib%2Fctools%2Fcss%2Fctools.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fcontrib%2Fdate%2Fdate_api%2Fdate.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fcontrib%2Fdate%2Fdate_popup%2Fthemes%2Fdatepicker.1.7.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fcontrib%2Ffield_group%2Ffield_group.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fcontrib%2Ffind_content%2Ffind_content.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fmodules%2Fcontrib%2Fviews%2Fcss%2Fviews.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fthemes%2Fwieni-subtheme%2Fcss%2Fstyles-ieLT9.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fthemes%2Fwieni-subtheme%2Fcss%2Fstyles.css%5D': '1',
                    'ajax_page_state%5Bcss%5D%5Bsites%2Fall%2Fthemes%2Fwieni-subtheme%2Fformidabel%2Fcss%2Fformidabel.css%5D': '1',
                    'ajax_page_state%5Bjs%5D%5B0%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bmisc%2Fajax.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bmisc%2Fautocomplete.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bmisc%2Fdrupal.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bmisc%2Fjquery.cookie.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bmisc%2Fjquery.form.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bmisc%2Fjquery.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bmisc%2Fjquery.once.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bmisc%2Fprogress.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bmisc%2Ftextarea.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bpublic%3A%2F%2Flanguages%2Fnl_w8wnamYcai6yuvZ-M3BoNjzMAlUuidLcrpE24d8xEeE.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fcontrib%2Ffield_group%2Ffield_group.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Fcontrib%2Fgoogle_analytics%2Fgoogleanalytics.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Ffeatures%2Factivity%2Fjs%2Fauto-submit.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fmodules%2Ffeatures%2Fingredient%2Fjs%2Fauto-submit-ajax.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fthemes%2Fwieni-subtheme%2Fformidabel%2Fjs%2Fformidabel.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fthemes%2Fwieni-subtheme%2Fjs%2Fscript-all.js%5D': '1',
                    'ajax_page_state%5Bjs%5D%5Bsites%2Fall%2Fthemes%2Fwieni-subtheme%2Fjs%2Fscript-window-events.js%5D': '1',
                    'ajax_page_state%5Btheme%5D': 'wienisubtheme',
                    'ajax_page_state%5Btheme_token%5D': '9wwfj40LBxa2ZV4T_STcWKpJ_q4LvFqtlH_b_yQEDRs',
                    'allergy': '_none',
                    'cooking_time': '_none',
                    'difficulty': '_none',
                    'form_build_id': 'form-kOlBkHhJDRwA_Cua_mgLEt9Tx6t8jnRwcKdAz5LxcDM',
                    'form_id': 'ingredient_search_form',
                    'ingredient': '',
                    'page': page,
                    'redirect': '',
                    'region': '_none',
                    'types': '_none'}
        
        response = requests.post('http://www.evavzw.be/system/ajax', data=params)
         
        json_resp = json.loads(response.text)
        html_resp = bs4.BeautifulSoup(json_resp[1]['data'])
        
#         response = requests.get('http://www.evavzw.be/recepten/')
#         html_resp = bs4.BeautifulSoup(response.text)
        
        last_page = int(html_resp.find('li', class_='pager-last').find('a')['href'].split('page=')[-1])
        
        for recipe in html_resp.find_all('div', class_='field-name-title'):
            recipes += 1
            yield RecipePage(url=recipe.find('a')['href'])
        
        page += 1
        if page > last_page:
            break
        
    
    return

def scrape_recipes(url=None):
    # ALL THA RECIPES ARE MINE!!!
    scraper = get_user_model().objects.get(id=1)
    try:
        external_site = ExternalSite.objects.get(name="Eva vzw")
    except ExternalSite.DoesNotExist:
        external_site = ExternalSite(name="Eva vzw", url='http://www.evavzw.be')
        external_site.save()
    
    cuisines = {cuisine.name: cuisine for cuisine in Cuisine.objects.all()}
        
    recipe_pages = get_recipe_pages(url)
    
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
        
        if recipe_page.recipe_source is not None:
            if recipe.instructions is None:
                recipe.instructions = ''
            recipe.instructions += 'Source: %s\r\n' % recipe_page.recipe_source.strip()
        
        recipe.save()
        
        image = RecipeImage(incomplete_recipe=recipe, added_by=scraper, visible=True, w=None, h=1)
        image.image.save(file_name, files.File(lf))
        
        t_usess = []
        for recipe_ingredient in recipe_page.recipe_ingredients:
            parsed_ing_name = recipe_ingredient[0]
            parsed_amount = recipe_ingredient[1]
            parsed_unit_name = recipe_ingredient[2]
            
            fil = models.Q()
            for i in range(min(3, len(parsed_ing_name))):
                fil |= models.Q(name__iexact=parsed_ing_name[:len(parsed_ing_name) - i])
                fil |= models.Q(plural_name__iexact=parsed_ing_name[:len(parsed_ing_name) - i])
                fil |= models.Q(synonyms__name__iexact=parsed_ing_name[:len(parsed_ing_name) - i])
            try:
                ingredients = Ingredient.objects.filter(fil).distinct()
                if len(ingredients) > 1:
                    raise Exception('Multiple ingredients found: {} - {}'.format(parsed_ing_name, [ing.name for ing in ingredients]))
                ingredient = ingredients[0]
            except IndexError:
                ingredient = Ingredient.objects.dummy()
            
            
            if parsed_amount is None:
                unit = Unit.objects.get(name__icontains='snuifje')
                parsed_unit_name = 'snuifje'
                parsed_amount = 1
                if not ingredient.is_dummy():
                    if not ingredient.can_use_unit(unit):
                        unit = Unit.objects.get(name__icontains='scheut')
                        parsed_unit_name = 'scheut'
                        if not ingredient.can_use_unit(unit):
                            unit = None
                            parsed_amount = 0
                            parsed_unit_name = 'Geen eenheid opgegeven'
                            
            elif parsed_unit_name is None:
                unit = Unit.objects.get(name__icontains='stuk')
                parsed_unit_name = 'stuk'
            else:
                fil = models.Q()
                for i in range(min(4, len(parsed_unit_name))):
                    units = Unit.objects.filter(models.Q(name__istartswith=parsed_unit_name[:len(parsed_unit_name) - i]) | models.Q(short_name__istartswith=parsed_unit_name[:len(parsed_unit_name) - i])).distinct()
                    if len(units) <= 0:
                        continue
                    if len(units) > 1:
                        raise Exception('Multiple units found: {} - {}'.format(parsed_unit_name, [unit.name for unit in units]))
                    unit = units[0]
                    break
                else:
                    unit = None
            
            t_ingredient = TemporaryIngredient(ingredient=ingredient, name=parsed_ing_name)
            t_ingredient.save()
            
            t_unit = TemporaryUnit(unit=unit, name=parsed_unit_name)
            t_unit.save()
            
            t_uses = TemporaryUsesIngredient(recipe=recipe, ingredient=t_ingredient, amount=parsed_amount,
                                             unit=t_unit)
            t_usess.append(t_uses)
        
        TemporaryUsesIngredient.objects.bulk_create(t_usess)
        
        if recipe.is_convertible():
            recipe.convert()

def scrape_recipe(url):
    return scrape_recipes(url)       