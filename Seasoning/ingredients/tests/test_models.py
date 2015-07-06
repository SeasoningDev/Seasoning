'''
Created on Jul 5, 2015

@author: joep
'''
from django.test import TestCase
from django_dynamic_fixture import G
from ingredients.models import Ingredient, Country, TransportMethod,\
    AvailableInCountry
from datetime import date

class IngredientModelTest(TestCase):
    
    def test_footprint_basic(self):
        ingredient = G(Ingredient, base_footprint=1, type=Ingredient.BASIC)
        
        self.assertEqual(ingredient.footprint(), 1)
        
    def test_footprint_seasonal(self):
        ingredient = G(Ingredient, base_footprint=1, type=Ingredient.SEASONAL)
        country = G(Country, distance=1)
        tm = G(TransportMethod, emissions_per_km=1)
        G(AvailableInCountry, location=country, transport_method=tm, ingredient=ingredient, extra_production_footprint=0, 
          date_from=date(2000, 1, 1), date_until=date(2000, 12, 31))
        
        self.assertEqual(ingredient.footprint(), 2)
        


class AvailableInModelTest(TestCase):
    
    def test_transportation_footprint(self):
        country = G(Country, distance=1)
        tm = G(TransportMethod, emission_per_km=1)
        aic = G(AvailableInCountry, location=country, transport_method=tm, extra_production_footprint=0)
        
        self.assertEqual(aic.transportation_footprint(), 1)
    
    def test_transportation_footprint_extra(self):
        country = G(Country, distance=1)
        tm = G(TransportMethod, emission_per_km=1)
        aic = G(AvailableInCountry, location=country, transport_method=tm, extra_production_footprint=1)
        
        self.assertEqual(aic.transportation_footprint(), 1)
        self.assertEqual(aic.total_extra_footprint(), 2)
        
