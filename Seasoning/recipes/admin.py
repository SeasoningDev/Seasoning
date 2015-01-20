from django.contrib import admin
from recipes.models import Recipe, Cuisine, UsesIngredient, ExternalSite,\
    RecipeImage
from recipes.models.t_recipe import IncompleteRecipe, TemporaryUsesIngredient
from recipes.models.std import Aggregate

class UsesIngredientInline(admin.TabularInline):
    model = UsesIngredient
    readonly_fields=('footprint',)

class RecipeAdmin(admin.ModelAdmin):
    inlines = [ UsesIngredientInline, ]
    search_fields = ['name']
    list_display = ('__unicode__', 'external', 'accepted')
        
class TemporaryUsesIngredientInline(admin.TabularInline):
    model = TemporaryUsesIngredient
            
class IncompleteRecipeAdmin(admin.ModelAdmin):
    inlines = [TemporaryUsesIngredientInline, ]
    
    
admin.site.register(ExternalSite)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Cuisine)
admin.site.register(RecipeImage)
admin.site.register(IncompleteRecipe, IncompleteRecipeAdmin)
admin.site.register(Aggregate)