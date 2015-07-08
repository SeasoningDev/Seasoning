'''
Created on Jul 5, 2015

@author: joep
'''
from recipes.models import Recipe, Cuisine, UsesIngredient, RecipeDistribution
from administration.admin import seasoning_admin_site
from django.contrib import admin

class UsesIngredientInline(admin.TabularInline):
    
    model = UsesIngredient
    
class RecipeAdmin(admin.ModelAdmin):
    
    model = Recipe
    inlines = [UsesIngredientInline]
    
seasoning_admin_site.register(Cuisine)
seasoning_admin_site.register(Recipe, RecipeAdmin)
seasoning_admin_site.register(RecipeDistribution)
