'''
Created on Jul 5, 2015

@author: joep
'''
from django.contrib import admin
from recipes.models import Recipe

admin.site.register(Recipe)
