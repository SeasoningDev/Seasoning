'''
Created on Apr 2, 2015

@author: joep
'''
from django.core.management.base import BaseCommand
from recipes.models import RecipeDistribution, Recipe
import numpy

class Command(BaseCommand):
     
    def handle(self, *args, **options):
        RecipeDistribution.objects.all().delete()
        
        for course, _ in Recipe.COURSES:
            recipes = Recipe.objects.filter(course=course)
            
            if len(recipes) > 0:
                footprints = [recipe.cached_footprint for recipe in recipes]
                
                RecipeDistribution(course=course, parameter=RecipeDistribution.MEAN,
                                   parameter_value=numpy.mean(footprints)).save()
                RecipeDistribution(course=course, parameter=RecipeDistribution.STANDARD_DEVIATION,
                                   parameter_value=numpy.std(footprints)).save()
            
            else:
                RecipeDistribution(course=course, parameter=RecipeDistribution.MEAN,
                                   parameter_value=0).save()
                RecipeDistribution(course=course, parameter=RecipeDistribution.STANDARD_DEVIATION,
                                   parameter_value=0).save()
                
            
            