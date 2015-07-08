'''
Created on Jul 5, 2015

@author: joep
'''
from django.test import TestCase
from django_dynamic_fixture import G
from ingredients.models import Ingredient, Country, TransportMethod,\
    AvailableInCountry
import datetime

class IngredientModelTest(TestCase):
    
    def test_footprint_basic(self):
        ingredient = G(Ingredient, base_footprint=1, type=Ingredient.BASIC)
        
        self.assertEqual(ingredient.footprint(), 1)
        
    def test_footprint_seasonal(self):
        ingredient = G(Ingredient, base_footprint=1, type=Ingredient.SEASONAL)
        country = G(Country, distance=1)
        tm = G(TransportMethod, emissions_per_km=1)
        G(AvailableInCountry, location=country, transport_method=tm, ingredient=ingredient, extra_production_footprint=0, 
          date_from=datetime.date(2000, 5, 5), date_until=datetime.date(2000, 7, 7))
        
        self.assertEqual(ingredient.footprint(datetime.date(2013, 6, 6)), 2)
        
        country = G(Country, distance=10)
        G(AvailableInCountry, location=country, transport_method=tm, ingredient=ingredient, extra_production_footprint=0, 
          date_from=datetime.date(2000, 5, 5), date_until=datetime.date(2000, 7, 7))
        
        self.assertEqual(ingredient.footprint(datetime.date(2013, 6, 6)), 2)
        
        country = G(Country, distance=0)
        G(AvailableInCountry, location=country, transport_method=tm, ingredient=ingredient, extra_production_footprint=0, 
          date_from=datetime.date(2000, 1, 1), date_until=datetime.date(2000, 3, 3))
        
        self.assertEqual(ingredient.footprint(datetime.date(2013, 6, 6)), 2)
        


class AvailableInModelTest(TestCase):
    
    def setUp(self):
        self.test_today = datetime.date(2013, 5, 5)
        
    def test_innie(self):
        ing = G(Ingredient, preservability=0)
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 10, 1),
                  date_until=datetime.date(2014, 11, 1), ingredient=ing)
        
        self.assertTrue(avail.innie())
        self.assertFalse(avail.outie())
        
    def test_outie(self):
        ing = G(Ingredient, preservability=0)
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 11, 1),
                  date_until=datetime.date(2014, 10, 1), ingredient=ing)
        
        self.assertFalse(avail.innie())
        self.assertTrue(avail.outie())
        
        
        
    def test_is_active(self):
        avail = G(AvailableInCountry,
                  date_from=datetime.date(2013, 2, 2),
                  date_until=datetime.date(2013, 7, 7))
        self.assertTrue(avail.is_active(self.test_today))
        
    def test_not_active_before(self):
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 6, 6),
                  date_until=datetime.date(2013, 7, 7))
        self.assertFalse(avail.is_active(self.test_today))

    def test_not_active_after(self):        
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 2, 2),
                  date_until=datetime.date(2013, 3, 3))
        self.assertFalse(avail.is_active(self.test_today))

    def test_is_active_outie(self):        
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 4, 4),
                  date_until=datetime.date(2013, 1, 1))
        self.assertTrue(avail.is_active(self.test_today))

    def test_is_active_outie_second_interval(self):        
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 9, 9),
                  date_until=datetime.date(2013, 7, 7))
        self.assertTrue(avail.is_active(self.test_today))

    def test_not_active_outie(self):        
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 9, 9),
                  date_until=datetime.date(2013, 1, 1))
        self.assertFalse(avail.is_active(self.test_today))

    def test_is_active_edge_cases(self):    
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 5, 4),
                  date_until=datetime.date(2014, 5, 5))
        self.assertTrue(avail.is_active(self.test_today))
        
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 5, 5),
                  date_until=datetime.date(2014, 5, 4))
        self.assertTrue(avail.is_active(self.test_today))
    
    
    
    def test_days_since_active(self):
        avail = G(AvailableInCountry,
                  date_from=datetime.date(2013, 2, 2),
                  date_until=datetime.date(2013, 7, 7))
        self.assertEqual(avail.days_since_last_active(self.test_today), 0)
        
        self.assertEqual(avail.days_since_last_active(datetime.date(2013, 7, 9)), 2)
        
        self.assertEqual(avail.days_since_last_active(datetime.date(2013, 1, 10)), 187)
        
        
    
    def test_transportation_footprint(self):
        country = G(Country, distance=1)
        tm = G(TransportMethod, emissions_per_km=1)
        aic = G(AvailableInCountry, location=country, transport_method=tm, extra_production_footprint=0)
        
        self.assertEqual(aic.transportation_footprint(), 1)
    
    def test_transportation_footprint_extra(self):
        country = G(Country, distance=1)
        tm = G(TransportMethod, emissions_per_km=1)
        aic = G(AvailableInCountry, location=country, transport_method=tm, extra_production_footprint=1)
        
        self.assertEqual(aic.transportation_footprint(), 1)
        self.assertEqual(aic.total_extra_footprint(), 2)
        
