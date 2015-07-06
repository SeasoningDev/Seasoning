'''
Created on Jul 5, 2015

@author: joep
'''
from django.contrib import admin
from ingredients.models import Ingredient, AvailableInCountry, TransportMethod,\
    AvailableInSea, CanUseUnit, Unit

class CanUseUnitInline(admin.TabularInline):
    
    model = CanUseUnit
    
    

class AvailableInCountryInline(admin.TabularInline):
    
    model = AvailableInCountry



class IngredientAdmin(admin.ModelAdmin):
    
    search_fields = ['name']
    inlines = [CanUseUnitInline, AvailableInCountryInline]
    
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(AvailableInCountry)
admin.site.register(AvailableInSea)
admin.site.register(TransportMethod)
admin.site.register(Unit)