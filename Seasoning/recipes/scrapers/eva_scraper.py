import requests
from bs4 import BeautifulSoup
from recipes.models import ExternalSite, Cuisine, ScrapedRecipe, Recipe,\
    ScrapedUsesIngredient
import difflib
from django.db import models
from ingredients.models import Ingredient, Unit

class RecipePage(object):
    
    def __init__(self, url):
        self.url = 'http://www.evavzw.be{}'.format(url.replace('http://www.evavzw.be', ''))
        self._content = None
    
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
    
    
        
def get_recipe_pages(page):
    resp = requests.post('http://www.evavzw.be/system/ajax',
                          data={'allergy': '_none',
                                  'cooking_time': '_none',
                                  'difficulty': '_none',
                                  'form_build_id': 'form-hJVvTkJVMyOLuh17gCFwHrjjX_6Q9RsQd2YZlt-ujWc',
                                  'form_id': 'ingredient_search_form',
                                  'ingredient': '',
                                  'page': page,
                                  'region': '_none',
                                  'types': '_none'})
    
    recipes_html = None
    for result_dict in resp.json():
        if len(result_dict.get('data', '')) > 0:
            recipes_html = BeautifulSoup(result_dict['data'])
            break
        
    if recipes_html is None:
        return None
    
    for recipe_div in recipes_html.find_all(class_='node-recipe'):
        yield RecipePage(url=recipe_div.find('h3').find('a')['href'])



def scrape_recipes():
    # ALL THA RECIPES ARE MINE!!!
    try:
        external_site = ExternalSite.objects.get(name="Eva vzw")
    except ExternalSite.DoesNotExist:
        external_site = ExternalSite(name="Eva vzw", url='http://www.evavzw.be')
        external_site.save()
    
    cuisines = {cuisine.name: cuisine for cuisine in Cuisine.objects.all()}
    
    
    
    page = 1
    
    last_recipe_page_first_recipe_url = None
    while True:
        recipe_pages = list(get_recipe_pages(page))
        
        if recipe_pages[0].url == last_recipe_page_first_recipe_url:
            break
        
        last_recipe_page_first_recipe_url = recipe_pages[0].url
        
        for recipe_page in recipe_pages:
            # Match course
            recipe_course = None
            recipe_course_proposal = recipe_page.recipe_course
            try:
                if recipe_page.recipe_course is not None:
                    best = difflib.get_close_matches(recipe_page.recipe_course, [x[1] for x in Recipe.COURSES], 1, 0.8)[0]
                    
                    for code, course in Recipe.COURSES:
                        if best == course:
                            recipe_course = code
                            break
            except IndexError:
                pass
            
            # Match cuisine
            recipe_cuisine = None
            recipe_cuisine_proposal = None
            if recipe_page.recipe_cuisine is not None:
                try:
                    best = difflib.get_close_matches(recipe_page.recipe_cuisine, cuisines.keys(), 1, 0.8)[0]
                    
                    recipe_cuisine = cuisines[best]
                except IndexError:
                    recipe_cuisine_proposal = recipe_page.recipe_cuisine
            
            recipe = ScrapedRecipe(name=recipe_page.recipe_name,
                                   external=True, external_site=external_site, external_url=recipe_page.url, 
                                   course=recipe_course, course_proposal=recipe_course_proposal, 
                                   cuisine=recipe_cuisine, cuisine_proposal=recipe_cuisine_proposal,
                                   portions=recipe_page.recipe_portions, active_time=0,
                                   passive_time=0,
                                   image_url=recipe_page.recipe_image)
            
            recipe.save()
            
            scraped_uses_ingredients = []
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
                    ingredient = None
                
                amount = parsed_amount
                if parsed_amount is None:
                    unit = Unit.objects.get(name__icontains='snuifje')
                    amount = 1
                                
                elif parsed_unit_name is None:
                    unit = Unit.objects.get(name__icontains='stuk')
                    
                else:
                    fil = models.Q()
                    for i in range(min(4, len(parsed_unit_name))):
                        units = Unit.objects.filter(models.Q(name__istartswith=parsed_unit_name[:len(parsed_unit_name) - i]) | models.Q(short_name__istartswith=parsed_unit_name[:len(parsed_unit_name) - i])).distinct()
                        if len(units) <= 0:
                            continue
                        if len(units) > 1:
                            best = difflib.get_close_matches(parsed_unit_name, [unit.name for unit in units], 1, 0)[0]
                            units = list(filter(lambda unit: unit.name == best, units))
                        unit = units[0]
                        break
                    else:
                        unit = None
                
                scraped_uses_ingredient = ScrapedUsesIngredient(recipe=recipe, 
                                                                ingredient=ingredient, ingredient_proposal=parsed_ing_name,
                                                                amount=amount, amount_proposal=parsed_amount,
                                                                unit=unit, unit_proposal=parsed_unit_name)
                scraped_uses_ingredients.append(scraped_uses_ingredient)
            
            ScrapedUsesIngredient.objects.bulk_create(scraped_uses_ingredients)
        
        page += 1