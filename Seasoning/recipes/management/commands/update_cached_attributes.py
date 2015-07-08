'''
Created on Apr 2, 2015

@author: joep
'''
from django.core.management.base import BaseCommand
from recipes.models import Recipe

class Command(BaseCommand):
     
    def handle(self, *args, **options):
        for recipe in Recipe.objects.all():
            recipe.update_cached_attributes()
        
            