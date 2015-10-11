'''
Created on Jul 5, 2015

@author: joep
'''
from ingredients.models import Ingredient, AvailableInCountry, TransportMethod,\
    AvailableInSea, CanUseUnit, Unit, Synonym
from django.contrib import admin
from administration.admin import seasoning_admin_site

class SynonymInline(admin.TabularInline):
    
    model = Synonym
    
class CanUseUnitInline(admin.TabularInline):
    
    model = CanUseUnit

class AvailableInCountryInline(admin.TabularInline):
    
    model = AvailableInCountry



class IngredientAdmin(admin.ModelAdmin):
    
    search_fields = ['name']
    inlines = [SynonymInline, CanUseUnitInline, AvailableInCountryInline]
    
seasoning_admin_site.register(Ingredient, IngredientAdmin)
seasoning_admin_site.register(AvailableInCountry)
seasoning_admin_site.register(AvailableInSea)
seasoning_admin_site.register(TransportMethod)
seasoning_admin_site.register(Unit)
seasoning_admin_site.register(CanUseUnit)
seasoning_admin_site.register(Synonym)
