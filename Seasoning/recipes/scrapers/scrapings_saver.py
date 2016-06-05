'''
Created on Jul 9, 2015

@author: joep
'''
from recipes.models import ExternalSite, Cuisine, Recipe, ScrapedRecipe,\
    ScrapedUsesIngredient
import difflib
from django.db import models
from ingredients.models import Ingredient, Unit
from recipes.scrapers import eva_scraper, kriskookt_scraper, evassmulhuisje_scraper, veganchallenge_scraper, \
        dagelijksekost_scraper
from pip._vendor.distlib.compat import raw_input

EVA_SCRAPER, KRISKOOKT_SCRAPER, EVASSMULHUISJE_SCRAPER = 0, 1, 2
VEGANCHALLENGE_SCRAPER, DAGELIJKSEKOST_SCRAPER = 3, 4
INSTALLED_SCRAPERS = {
    DAGELIJKSEKOST_SCRAPER: {
        'id': DAGELIJKSEKOST_SCRAPER,
        'name': 'Dagelijkse Kost',
        'image': 'https://images.tvgemist.be/images/programs/dagelijkse-kost.jpg',
        'color': '#a9cfdd',

        'recipes': ScrapedRecipe.objects.filter(external_site__name__exact='Dagelijkse Kost'),
        'scraper': dagelijksekost_scraper.get_recipe_pages
    },
#    EVA_SCRAPER: {'name': 'Eva vzw',
#                  'scraper': eva_scraper.get_recipe_pages},
#    KRISKOOKT_SCRAPER: {'name': 'Kris kookt',
#                        'scraper': kriskookt_scraper.get_recipe_pages},
#    EVASSMULHUISJE_SCRAPER: {'name': 'Eva\'s Smulhuisje',
#                             'scraper': evassmulhuisje_scraper.get_recipe_pages},
#    VEGANCHALLENGE_SCRAPER: {'name': 'VeganChallenge',
#                             'scraper': veganchallenge_scraper.get_recipe_pages}}
}

def scrape_recipes(scraper):
    # ALL THA RECIPES ARE MINE!!!
    if scraper not in INSTALLED_SCRAPERS:
        raise Exception('Scraper {} not installed'.format(scraper))
    
    scraper_properties = INSTALLED_SCRAPERS[scraper]
    external_site = ExternalSite.objects.get(name=scraper_properties['name'])
    get_recipe_pages = scraper_properties['scraper']
    
    cuisines = {cuisine.name: cuisine for cuisine in Cuisine.objects.all()}
    
    
    
    for recipe_page in get_recipe_pages():
        print(recipe_page.recipe_name)
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
        
            recipe = ScrapedRecipe(name=recipe_page.recipe_name, scraped_name=recipe_page.recipe_name,
                                   description=recipe_page.recipe_description,
                                   external=True, external_site=external_site, external_url=recipe_page.url, 
                                   course=recipe_course, course_proposal=recipe_course_proposal, 
                                   cuisine=recipe_cuisine, cuisine_proposal=recipe_cuisine_proposal,
                                   portions=recipe_page.recipe_portions, active_time=0,
                                   passive_time=0,
                                   image_url=recipe_page.recipe_image)
            
        except NotImplementedError:
            print('Could not scrape recipe on page `{}`'.format(recipe_page.url))
            continue
        
        recipe.save()
        
        scraped_uses_ingredients = []
        for ingredient_line, amount, unit, ingredient in recipe_page.recipe_ingredients:
            scraped_uses_ingredient = ScrapedUsesIngredient(
                    recipe=recipe,
                    raw_ingredient_line=ingredient_line,
                    ingredient=ingredient,
                    amount=amount,
                    unit=unit)
            scraped_uses_ingredients.append(scraped_uses_ingredient)
        
        ScrapedUsesIngredient.objects.bulk_create(scraped_uses_ingredients)
        
