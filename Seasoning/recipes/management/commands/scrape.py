'''
Created on Apr 2, 2015

@author: joep
'''
from django.core.management.base import BaseCommand
from recipes.models import Recipe
from recipes.scrapers.scrapings_saver import INSTALLED_SCRAPERS, scrape_recipes

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('scraper_id', type=int)

    def handle(self, *args, **options):
        if 'scraper_id' not in options:
            print('Please provide a scraper id:')
            for scraper_id in INSTALLED_SCRAPERS.keys().sorted():
                print('{}: {}'.format(scraper_id, INSTALLED_SCRAPERS[scraper_id]))
            return

        scrape_recipes(options['scraper_id'])
            
