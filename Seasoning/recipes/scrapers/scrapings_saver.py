'''
Created on Jul 9, 2015

@author: joep
'''
from recipes.models import ExternalSite, Cuisine, Recipe, ScrapedRecipe,\
    ScrapedUsesIngredient
import difflib
from django.db import models
from ingredients.models import Ingredient, Unit
from recipes.scrapers import eva_scraper, kriskookt_scraper, evassmulhuisje_scraper
from pip._vendor.distlib.compat import raw_input

EVA_SCRAPER, KRISKOOKT_SCRAPER, EVASSMULHUISJE_SCRAPER = 0, 1, 2
INSTALLED_SCRAPERS = {
    EVA_SCRAPER: {'name': 'Eva vzw',
                  'scraper': eva_scraper.get_recipe_pages},
    KRISKOOKT_SCRAPER: {'name': 'Kris kookt',
                        'scraper': kriskookt_scraper.get_recipe_pages},
    EVASSMULHUISJE_SCRAPER: {'name': 'Eva\'s Smulhuisje',
                             'scraper': evassmulhuisje_scraper.get_recipe_pages}}
    
def scrape_recipes(scraper):
    # ALL THA RECIPES ARE MINE!!!
    if scraper not in INSTALLED_SCRAPERS:
        raise Exception('Scraper {} not installed'.format(scraper))
    
    scraper_properties = INSTALLED_SCRAPERS[scraper]
    external_site = ExternalSite.objects.get(name=scraper_properties['name'])
    get_recipe_pages = scraper_properties['scraper']
    
    cuisines = {cuisine.name: cuisine for cuisine in Cuisine.objects.all()}
    
    
    
    for recipe_page in get_recipe_pages():
        if ScrapedRecipe.objects.filter(external_site=external_site,
                                        scraped_name=recipe_page.recipe_name).exists():
            
            print('Skipped `{}` ({}), already scraped'.format(recipe_page.recipe_name, external_site.name))
            continue
            
        try:
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
                    
            if len(list(recipe_page.recipe_ingredients)) <= 0:
                raise NotImplementedError
            
        except NotImplementedError:
            print('Could not scrape recipe on page `{}`'.format(recipe_page.url))
            continue
        
        recipe = ScrapedRecipe(name=recipe_page.recipe_name, scraped_name=recipe_page.recipe_name,
                               description=recipe_page.recipe_description,
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
            parsed_group_name = recipe_ingredient[3]
            
            fil = models.Q()
            for i in range(min(3, len(parsed_ing_name))):
                fil |= models.Q(name__iexact=parsed_ing_name[:len(parsed_ing_name) - i])
                fil |= models.Q(plural_name__iexact=parsed_ing_name[:len(parsed_ing_name) - i])
                fil |= models.Q(synonyms__name__iexact=parsed_ing_name[:len(parsed_ing_name) - i])
            try:
                ingredients = Ingredient.objects.filter(fil).distinct()
                if len(ingredients) > 1:
                    best = difflib.get_close_matches(parsed_ing_name, [ing.name for ing in ingredients], 1, 0)[0]
                    ingredients = list(filter(lambda ing: ing.name == best, ingredients))

                ingredient = ingredients[0]
            except IndexError:
                ingredient = None
            
            amount = parsed_amount
            if '/' in str(amount) or '⁄' in str(amount):
                parts = amount.split('/') if '/' in str(amount) else amount.split('⁄')
                if len(parts) > 1 and parts[1] != '':
                    amount = int(parts[0]) / float(parts[1])
                else:
                    
                    amount = int(parts[0]) / 2.0
                    
            if ',' in str(amount):
                amount = amount.replace(',', '.')
            
            if 'ml' in str(amount):
                amount = amount.replace('ml', '')
                if parsed_unit_name is None:
                    parsed_unit_name = 'ml'
            
            elif 'l' in str(amount):
                amount = amount.replace('l', '')
                if amount is None:
                    amount = 'l'
            
            if 'g' in str(amount):
                amount = amount.replace('g', '')
                amount = amount.replace('r', '')
                if parsed_unit_name is None:
                    parsed_unit_name = 'gram'
            
            if '-' in str(amount):
                amount = amount.split('-')[-1]
                
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
                                                            unit=unit, unit_proposal=parsed_unit_name,
                                                            group=parsed_group_name)
            scraped_uses_ingredients.append(scraped_uses_ingredient)
        
        ScrapedUsesIngredient.objects.bulk_create(scraped_uses_ingredients)
        