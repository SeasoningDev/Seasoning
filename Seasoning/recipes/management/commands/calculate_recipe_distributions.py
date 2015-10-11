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
        
        footprints = [f[0] for f in Recipe.objects.all().values_list('cached_footprint')]
        RecipeDistribution(group=RecipeDistribution.ALL, parameter=RecipeDistribution.MEAN,
                           parameter_value=numpy.mean(footprints)).save()
        RecipeDistribution(group=RecipeDistribution.ALL, parameter=RecipeDistribution.STANDARD_DEVIATION,
                           parameter_value=numpy.std(footprints)).save()
        
        for course, _ in Recipe.COURSES:
            footprints =  [f[0] for f in Recipe.objects.filter(course=course).values_list('cached_footprint')]
            
            if len(footprints) > 0:
                RecipeDistribution(group=course, parameter=RecipeDistribution.MEAN,
                                   parameter_value=numpy.mean(footprints)).save()
                RecipeDistribution(group=course, parameter=RecipeDistribution.STANDARD_DEVIATION,
                                   parameter_value=numpy.std(footprints)).save()
            
            else:
                RecipeDistribution(group=course, parameter=RecipeDistribution.MEAN,
                                   parameter_value=0).save()
                RecipeDistribution(group=course, parameter=RecipeDistribution.STANDARD_DEVIATION,
                                   parameter_value=0).save()
                
            
            