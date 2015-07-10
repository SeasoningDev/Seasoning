'''
Created on Jul 5, 2015

@author: joep
'''
from recipes.models import Recipe, Cuisine, UsesIngredient, RecipeDistribution,\
    ExternalSite, ScrapedRecipe, ScrapedUsesIngredient
from administration.admin import seasoning_admin_site
from django.contrib import admin

class UsesIngredientInline(admin.TabularInline):
    
    model = UsesIngredient
    
class RecipeAdmin(admin.ModelAdmin):
    
    model = Recipe
    inlines = [UsesIngredientInline]
    
class ScrapedUsesIngredientInline(admin.TabularInline):
    
    model = ScrapedUsesIngredient
    
class ScrapedRecipeAdmin(admin.ModelAdmin):
    
    model = ScrapedRecipe
    inlines = [ScrapedUsesIngredientInline]
    
seasoning_admin_site.register(Cuisine)
seasoning_admin_site.register(Recipe, RecipeAdmin)
seasoning_admin_site.register(RecipeDistribution)
seasoning_admin_site.register(ExternalSite)
seasoning_admin_site.register(ScrapedRecipe, ScrapedRecipeAdmin)
