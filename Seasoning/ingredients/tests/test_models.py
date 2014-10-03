import datetime
import ingredients
from django.test import TestCase
from django_dynamic_fixture import G
from ingredients.tests import test_datetime
from ingredients.models import Unit, Country, Ingredient, AvailableInCountry, TransportMethod, AvailableIn, CanUseUnit, AvailableInSea

# All calls to datetime.date.today within ingredients.models will
# return 2013-05-05 as the current date
ingredients.models.units.datetime = test_datetime.TestDatetime()
ingredients.models.availability.datetime = test_datetime.TestDatetime()
ingredients.models.ingredients.datetime = test_datetime.TestDatetime()

"""
ingredients.models.units

"""
class UnitModelTestCase(TestCase):
    pass

class CanUseUnitModelTestCase(TestCase):
    
    def setUp(self):
        self.ing = G(Ingredient)
        self.unit1 = G(Unit, parent_unit=None)
        self.unit2 = G(Unit, parent_unit=self.unit1, ratio=0.1)
    
    def test_save(self):
        ing1 = G(Ingredient)
        
        G(CanUseUnit, unit=self.unit2, ingredient=ing1)
        
        ing1.canuseunit_set.get(unit=self.unit2)
        self.assertRaises(CanUseUnit.DoesNotExist, lambda: ing1.canuseunit_set.get(unit=self.unit1))
        
        ing2 = G(Ingredient)
        
        G(CanUseUnit, unit=self.unit1, ingredient=ing2)
        ing2.canuseunit_set.get(unit=self.unit1)
        ing2.canuseunit_set.get(unit=self.unit2)
    
    def test_delete(self):
        ing = G(Ingredient)
        
        cuu1 = G(CanUseUnit, unit=self.unit1, ingredient=ing)
        cuu1.delete()
        
        self.assertRaises(CanUseUnit.DoesNotExist, lambda: ing.canuseunit_set.get(unit=self.unit1))
        self.assertRaises(CanUseUnit.DoesNotExist, lambda: ing.canuseunit_set.get(unit=self.unit2))
        
        G(CanUseUnit, unit=self.unit1, ingredient=ing)
        
        cuu2 = CanUseUnit.objects.get(unit=self.unit2, ingredient=ing)
        
        cuu2.delete()
        
        self.assertRaises(CanUseUnit.DoesNotExist, lambda: ing.canuseunit_set.get(unit=self.unit1))
        self.assertRaises(CanUseUnit.DoesNotExist, lambda: ing.canuseunit_set.get(unit=self.unit2))
        


"""
ingredients.models.availability

"""
class CountryModelTestCase(TestCase):
    pass

class SeaModelTestCase(TestCase):
    pass

class TransportMethodModelTestCase(TestCase):
    pass

class AvailableInModelTestCase(TestCase):
    
    def test_full_date_until(self):
        # No preservability
        ing = G(Ingredient, preservability=0)
        avail = G(AvailableInCountry, ingredient=ing)
        
        self.assertEqual(avail.date_until, avail.full_date_until())
        
        # Basic preservability
        ing = G(Ingredient, type=Ingredient.SEASONAL, preservability=10)
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 1, 1), 
                  date_until=datetime.date(2014, 2, 1), ingredient=ing)
        
        self.assertEqual((avail.full_date_until() - avail.date_until).days, ing.preservability)
        self.assertEqual(avail.full_date_until().year, AvailableIn.BASE_YEAR)
        
        # Preservability make full_date_until wrap around year
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 10, 1),
                  date_until=datetime.date(2014, 12, 30), ingredient=ing)
        
        self.assertEqual(AvailableIn.DAYS_IN_BASE_YEAR - (avail.date_until - avail.full_date_until()).days, ing.preservability)
        self.assertEqual(avail.full_date_until().year, AvailableIn.BASE_YEAR)
        
        # Preservability makes full_date_until wrap over date_from
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 10, 30),
                  date_until=datetime.date(2014, 10, 25), ingredient=ing)
        
        self.assertEqual((avail.date_from - avail.full_date_until()).days, 1)
        
        # Combination of previous 2
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 1, 3),
                  date_until=datetime.date(2014, 12, 30), ingredient=ing)
        
        self.assertEqual(avail.full_date_until(), avail.date_from - datetime.timedelta(days=1))
    
    def test_innie_outie(self):
        ing = G(Ingredient, preservability=0)
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 10, 1),
                  date_until=datetime.date(2014, 11, 1), ingredient=ing)
        
        self.assertTrue(avail.innie())
        self.assertFalse(avail.outie())
        
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 11, 1),
                  date_until=datetime.date(2014, 10, 1), ingredient=ing)
        
        self.assertFalse(avail.innie())
        self.assertTrue(avail.outie())
        
    def test_is_active(self):
        # Standard
        avail = G(AvailableInCountry,
                  date_from=datetime.date(2013, 2, 2),
                  date_until=datetime.date(2013, 7, 7))
        self.assertTrue(avail.is_active())
        self.assertTrue(avail.is_active(test_datetime.TestDatetime().date.today()))
        
        # Standard not active (date is before interval)
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 6, 6),
                  date_until=datetime.date(2013, 7, 7))
        self.assertFalse(avail.is_active())
        
        # Standard not active (date is after interval)
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 2, 2),
                  date_until=datetime.date(2013, 3, 3))
        self.assertFalse(avail.is_active())
        
        # Outie interval active
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 4, 4),
                  date_until=datetime.date(2013, 1, 1))
        self.assertTrue(avail.is_active())
        
        # Outie interval 2 active
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 9, 9),
                  date_until=datetime.date(2013, 7, 7))
        self.assertTrue(avail.is_active())
        
        # Outie interval not active
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 9, 9),
                  date_until=datetime.date(2013, 1, 1))
        self.assertFalse(avail.is_active())
    
        # Edge cases
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 5, 4),
                  date_until=datetime.date(2014, 5, 5))
        self.assertTrue(avail.is_active())
        
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 5, 5),
                  date_until=datetime.date(2014, 5, 4))
        self.assertTrue(avail.is_active())
        
    def test_under_preservation(self):
        ingnp = G(Ingredient, preservability=0)
        ingp = G(Ingredient, type=Ingredient.SEASONAL, preservability=30)
        
        # Innie
        availnp = G(AvailableInCountry, date_from=datetime.date(2014, 1, 1),
                  date_until=datetime.date(2014, 5, 1), ingredient=ingnp)
        availp = G(AvailableInCountry, date_from=datetime.date(2014, 1, 1),
                  date_until=datetime.date(2014, 5, 1), ingredient=ingp)
        self.assertFalse(availnp.under_preservation())
        self.assertTrue(availp.under_preservation())
        
        # Outie
        availnp = G(AvailableInCountry, date_from=datetime.date(2014, 10, 1),
                  date_until=datetime.date(2014, 5, 1), ingredient=ingnp)
        availp = G(AvailableInCountry, date_from=datetime.date(2014, 10, 1),
                  date_until=datetime.date(2014, 5, 1), ingredient=ingp)
        self.assertFalse(availnp.under_preservation())
        self.assertTrue(availp.under_preservation())
    
    def test_days_preserving(self):
        ing = G(Ingredient, type=Ingredient.SEASONAL, preservability=30)
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 1, 1),
                  date_until=datetime.date(2014, 5, 1), ingredient=ing)
        
        self.assertEqual(avail.days_preserving(), 4)
        
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 10, 1),
                  date_until=datetime.date(2014, 12, 20), ingredient=ing)
        
        self.assertEqual(avail.days_preserving(date=datetime.date(2014, 1, 1)), 12)
    
    def test_footprint(self):
        # Not under preservation
        ing = G(Ingredient, type=Ingredient.SEASONAL, preservability=0)
        
        # No extra footprint
        c = G(Country, distance=1000)
        tm = G(TransportMethod, emission_per_km=1)
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 1, 1),
                  date_until=datetime.date(2014, 5, 10), ingredient=ing,
                  location=c, transport_method=tm, extra_production_footprint=0)
        
        self.assertEqual(avail.footprint(), 1000)
        
        # Country distance = 0
        c = G(Country, distance=0)
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 1, 1),
                  date_until=datetime.date(2014, 5, 10), ingredient=ing,
                  location=c, transport_method=tm, extra_production_footprint=10)
        
        self.assertEqual(avail.footprint(), 10)
        
        # No transportation footprint (impossible, but just to check)
        c = G(Country, distance=1000)
        tm = G(TransportMethod, emission_per_km=0)
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 1, 1),
                  date_until=datetime.date(2014, 5, 10), ingredient=ing,
                  location=c, transport_method=tm, extra_production_footprint=10)
        
        self.assertEqual(avail.footprint(), 10)
        
        # Under preservation
        ing = G(Ingredient, type=Ingredient.SEASONAL, base_footprint=6,
                preservability=30, preservation_footprint=1)
        c = G(Country, distance=0)
        avail = G(AvailableInCountry, date_from=datetime.date(2014, 1, 1),
                  date_until=datetime.date(2014, 5, 1), ingredient=ing,
                  location=c, transport_method=tm, extra_production_footprint=0)
        
        self.assertEqual(avail.footprint(), 4)
        
        self.assertEqual(avail.full_footprint(), 10)
        
    def test_save(self):
        avail = G(AvailableInCountry,
                  date_from=datetime.date(2013, 2, 2),
                  date_until=datetime.date(2013, 7, 7))
        
        self.assertEqual(avail.date_from.year, AvailableIn.BASE_YEAR)
        self.assertEqual(avail.date_until.year, AvailableIn.BASE_YEAR)


"""
ingredients.models.ingredients

"""
class IngredientModelTestCase(TestCase):
    
    def test_primary_unit(self):
        ing = G(Ingredient)
        self.assertEqual(ing.primary_unit, None)
        
        G(CanUseUnit, ingredient=ing)
        self.assertEqual(ing.primary_unit, None)
        
        pu = G(CanUseUnit, ingredient=ing, is_primary_unit=True).unit
        self.assertEqual(ing.primary_unit, pu)
    
    def test_can_use_unit(self):
        punit = G(Unit)
        unit = G(Unit, parent_unit=punit)
        ing = G(Ingredient)
        self.assertFalse(ing.can_use_unit(punit))
        
        G(CanUseUnit, ingredient=ing, unit=punit)
        self.assertTrue(ing.can_use_unit(punit))
        self.assertTrue(ing.can_use_unit(unit))
        
    def test_get_available_ins(self):
        bing = G(Ingredient, type=Ingredient.BASIC)
        
        sing = G(Ingredient, type=Ingredient.SEASONAL)
        self.assertEqual(len(sing.get_available_ins()), 0)
        
        G(AvailableInCountry, ingredient=sing)
        G(AvailableInCountry, ingredient=sing)
        
        ssing = G(Ingredient, type=Ingredient.SEASONAL_SEA)
        self.assertEqual(len(ssing.get_available_ins()), 0)
        
        G(AvailableInSea, ingredient=ssing)
        G(AvailableInSea, ingredient=ssing)
        G(AvailableInSea, ingredient=ssing)
        
        self.assertRaises(Ingredient.BasicIngredientException, bing.get_available_ins)
        self.assertEqual(len(sing.get_available_ins()), 2)
        self.assertEqual(len(ssing.get_available_ins()), 3)
        
    def test_get_active_available_ins(self):
        ing = G(Ingredient, type=Ingredient.SEASONAL, preservability=0)
        self.assertEqual(len(ing.get_active_available_ins()), 0)
                
        G(AvailableInCountry, ingredient=ing,
          date_from=datetime.date(2013, 2, 2),
          date_until=datetime.date(2013, 3, 3))
        self.assertEqual(len(ing.get_active_available_ins()), 0)
                
        G(AvailableInCountry, ingredient=ing,
          date_from=datetime.date(2013, 2, 2),
          date_until=datetime.date(2013, 7, 7))
        self.assertEqual(len(ing.get_active_available_ins()), 1)
    
    def test_get_available_in_with_smallest_footprint(self):
        ing = G(Ingredient, type=Ingredient.SEASONAL, preservability=50,
                base_footprint=5, preservation_footprint=10)
        country = G(Country, distance=10)
        tpm = G(TransportMethod, emission_per_km=20)
        avail1 = G(AvailableInCountry, ingredient=ing, location=country,
                   transport_method=tpm, extra_production_footprint=500,
                   date_from=datetime.date(2013, 2, 2),
                   date_until=datetime.date(2013, 7, 7))
        self.assertEqual(ing.get_available_in_with_smallest_footprint(), avail1)
        
        G(AvailableInCountry, ingredient=ing, location=country,
          transport_method=tpm, extra_production_footprint=501,
          date_from=datetime.date(2013, 2, 2),
          date_until=datetime.date(2013, 7, 7))
        self.assertEqual(ing.get_available_in_with_smallest_footprint(), avail1)
        
        avail2 = G(AvailableInCountry, ingredient=ing, location=country,
                   transport_method=tpm, extra_production_footprint=499,
                   date_from=datetime.date(2013, 2, 2),
                   date_until=datetime.date(2013, 7, 7))
        self.assertEqual(ing.get_available_in_with_smallest_footprint(), avail2)
        
        # preservation footprint makes it higher than previous
        G(AvailableInCountry, ingredient=ing, location=country,
          transport_method=tpm, extra_production_footprint=498,
          date_from=datetime.date(2013, 2, 2),
          date_until=datetime.date(2013, 4, 4))
        self.assertEqual(ing.get_available_in_with_smallest_footprint(), avail2)
        
        # preservation footprint makes it higher, but reduced extra_production_footprint
        # makes it lower than avail2
        avail3 = G(AvailableInCountry, ingredient=ing, location=country,
                   transport_method=tpm, extra_production_footprint=100,
                   date_from=datetime.date(2013, 2, 2),
                   date_until=datetime.date(2013, 4, 4))
        self.assertEqual(ing.get_available_in_with_smallest_footprint(), avail3)
        
    def test_always_available(self):
        ing = G(Ingredient, type=Ingredient.SEASONAL, preservability=50)
        self.assertFalse(ing.always_available())
        
        G(AvailableInCountry, ingredient=ing,
          date_from=datetime.date(2013, 2, 2),
          date_until=datetime.date(2013, 10, 2))
        self.assertFalse(ing.always_available())
        
        G(AvailableInCountry, ingredient=ing,
          date_from=datetime.date(2013, 10, 3),
          date_until=datetime.date(2013, 2, 1))
        self.assertTrue(ing.always_available())
        
        # Preservability pushes until date over edge
        ing2 = G(Ingredient, type=Ingredient.SEASONAL, preservability=91)
        G(AvailableInCountry, ingredient=ing2,
          date_from=datetime.date(2013, 6, 1),
          date_until=datetime.date(2013, 7, 31))
        G(AvailableInCountry, ingredient=ing2,
          date_from=datetime.date(2013, 8, 1),
          date_until=datetime.date(2013, 12, 31))
        self.assertFalse(ing2.always_available())
        
        G(AvailableInCountry, ingredient=ing2,
          date_from=datetime.date(2013, 4, 1),
          date_until=datetime.date(2013, 5, 31))
        self.assertTrue(ing2.always_available())
    
    def test_footprint(self):
        bing = G(Ingredient, type=Ingredient.BASIC)
        self.assertEqual(bing.footprint(), bing.base_footprint)
        
        sing = G(Ingredient, type=Ingredient.SEASONAL, preservability=200,
                 preservation_footprint=10, base_footprint=100)
        country = G(Country, distance=10)
        tpm = G(TransportMethod, emission_per_km=20)
        avail1 = G(AvailableInCountry, ingredient=sing, location=country,
                   transport_method=tpm, extra_production_footprint=5000,
                   date_from=datetime.date(2013, 2, 2),
                   date_until=datetime.date(2013, 7, 7))        
        self.assertEqual(sing.footprint(), avail1.full_footprint())
        
        avail2 = G(AvailableInCountry, ingredient=sing, location=country,
                   transport_method=tpm, extra_production_footprint=0,
                   date_from=datetime.date(2013, 7, 1),
                   date_until=datetime.date(2013, 12, 1))
        self.assertEqual(sing.footprint(), avail2.full_footprint())
        
        avail3 = G(AvailableInCountry, ingredient=sing, location=country,
                    transport_method=tpm, extra_production_footprint=100,
                    date_from=datetime.date(2013, 2, 2),
                    date_until=datetime.date(2013, 5, 1))
        self.assertEqual(sing.footprint(), avail3.full_footprint())
        
    def test_coming_from_endangered(self):
        ing = G(Ingredient, type=Ingredient.SEASONAL_SEA)
        G(AvailableInSea, ingredient=ing, date_from=datetime.date(2013, 2, 2),
                    date_until=datetime.date(2013, 5, 10), endangered=False)
        
        self.assertFalse(ing.coming_from_endangered())
        
        G(AvailableInSea, ingredient=ing, date_from=datetime.date(2013, 2, 2),
                    date_until=datetime.date(2013, 5, 10), endangered=True)
        
        self.assertTrue(ing.coming_from_endangered())
        
        
    def test_save(self):
        bing = G(Ingredient, type=Ingredient.BASIC, preservability=10,
                 preservation_footprint=100, base_footprint=1, accepted=True)
        self.assertEqual(bing.preservability, 0)
        self.assertEqual(bing.preservation_footprint, 0)

class SynonymModelTestCase(TestCase):
    pass
