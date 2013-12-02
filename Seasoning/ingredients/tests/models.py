from django.test import TestCase
import ingredients.models
from ingredients.models import Unit, Country, Ingredient, AvailableInCountry, TransportMethod, AvailableIn, CanUseUnit, AvailableInSea
import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django_dynamic_fixture import G
from ingredients.tests import test_datetime
from general.decorators import mysqldb_required
from recipes.models import Recipe, UsesIngredient, Cuisine

# All calls to datetime.date.today within ingredients.models will
# return 2013-05-05 as the current date
ingredients.models.datetime = test_datetime.TestDatetime()

class UnitModelTestCase(TestCase):
    pass

class SynonymModelTestCase(TestCase):
    pass

class CountryModelTestCase(TestCase):
    pass

class SeaModelTestCase(TestCase):
    pass

class TransportMethodModelTestCase(TestCase):
    pass

class CanUseUnitModelTestCase(TestCase):
    pass

class CanUseUnitManagerTestCase(TestCase):
    
    @mysqldb_required
    def test_useable_by(self):
        punit = G(Unit)        
        cunit = G(Unit, parent_unit=punit)
        unit = G(Unit)
        G(Unit)
        
        cuu = G(CanUseUnit, unit=punit)
        ing = cuu.ingredient
        G(CanUseUnit, ingredient=ing, unit=unit)
        
        cuus = ing.canuseunit_set.all()
        
        self.assertEqual(len(list(cuus)), 3)
        self.assertTrue(punit in [x.unit for x in cuus])
        self.assertTrue(cunit in [x.unit for x in cuus])
        self.assertTrue(unit in [x.unit for x in cuus])
        
        cuus = ing.canuseunit_set.all()
        
        self.assertEqual(len(list(cuus)), 3)

class AvailableInModelTestCase(TestCase):
        
    def test_save(self):
        ing = G(Ingredient, base_footprint=5)
        country = G(Country, distance=10)
        tpm = G(TransportMethod, emission_per_km=20)
        avail = G(AvailableInCountry, location=country, transport_method=tpm,
                  extra_production_footprint=30, ingredient=ing,
                  date_from=datetime.date(2013, 2, 2),
                  date_until=datetime.date(2013, 7, 7))
        
        self.assertEqual(avail.date_from.year, AvailableIn.BASE_YEAR)
        self.assertEqual(avail.date_until.year, AvailableIn.BASE_YEAR)
        self.assertEqual(avail.footprint, 5 + 10*20 + 30)
    
    def test_is_active(self):
        avail = G(AvailableInCountry,
                  date_from=datetime.date(2013, 2, 2),
                  date_until=datetime.date(2013, 7, 7))
        self.assertTrue(avail.is_active())
        self.assertTrue(avail.is_active(test_datetime.TestDatetime().date.today()))
        
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 6, 6),
                  date_until=datetime.date(2013, 7, 7))
        self.assertFalse(avail.is_active())
        
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 2, 2),
                  date_until=datetime.date(2013, 3, 3))
        self.assertFalse(avail.is_active())
        
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 4, 4),
                  date_until=datetime.date(2013, 1, 1))
        self.assertTrue(avail.is_active())
        
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 9, 9),
                  date_until=datetime.date(2013, 7, 7))
        self.assertTrue(avail.is_active())
        
        avail = G(AvailableInCountry, 
                  date_from=datetime.date(2013, 9, 9),
                  date_until=datetime.date(2013, 1, 1))
        self.assertFalse(avail.is_active())
    
    def test_is_active_extension(self):
        avail = G(AvailableInCountry,
                  date_from=datetime.date(2013, 2, 2),
                  date_until=datetime.date(2013, 5, 1))
        self.assertTrue(avail.is_active(date_until_extension=4))
        self.assertTrue(avail.is_active(date_until_extension=40))
        self.assertTrue(avail.is_active(date_until_extension=400))
        
        avail = G(AvailableInCountry,
                  date_from=datetime.date(2013, 12, 10),
                  date_until=datetime.date(2013, 12, 15))
        self.assertTrue(avail.is_active(date_until_extension=200))
        self.assertTrue(avail.is_active(date_until_extension=400))
        
        avail = G(AvailableInCountry,
                  date_from=datetime.date(2013, 12, 10),
                  date_until=datetime.date(2013, 5, 1))
        self.assertTrue(avail.is_active(date_until_extension=4))
        self.assertTrue(avail.is_active(date_until_extension=40))
        self.assertTrue(avail.is_active(date_until_extension=400))
    
    def test_days_apart(self):
        avail = G(AvailableInCountry,
                  date_from=datetime.date(2013, 5, 1),
                  date_until=datetime.date(2013, 5, 1))
        
        date = datetime.date(2010, 5, 5)
        self.assertEqual(avail.days_apart(date), 4)
        
        date = datetime.date(2010, 5, 1)
        self.assertEqual(avail.days_apart(date), 0)
        
        date = datetime.date(2010, 4, 30)
        self.assertEqual(avail.days_apart(date), 364)
        
        avail = G(AvailableInCountry,
                  date_from=datetime.date(2013, 5, 10),
                  date_until=datetime.date(2013, 5, 1))
        
        date = datetime.date(2010, 5, 5)
        self.assertEqual(avail.days_apart(date), 4)
        
        date = datetime.date(2010, 5, 1)
        self.assertEqual(avail.days_apart(date), 0)

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
        ing2 = G(Ingredient, type=Ingredient.SEASONAL, preservability=90)
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
                 preservation_footprint=10)
        country = G(Country, distance=10)
        tpm = G(TransportMethod, emission_per_km=20)
        avail1 = G(AvailableInCountry, ingredient=sing, location=country,
                   transport_method=tpm, extra_production_footprint=5000,
                   date_from=datetime.date(2013, 2, 2),
                   date_until=datetime.date(2013, 7, 7))        
        self.assertEqual(sing.footprint(), avail1.footprint)
        
        avail2 = G(AvailableInCountry, ingredient=sing, location=country,
                   transport_method=tpm, extra_production_footprint=0,
                   date_from=datetime.date(2013, 7, 1),
                   date_until=datetime.date(2013, 12, 1))
        self.assertEqual(sing.footprint(), avail2.footprint + 155*sing.preservation_footprint)
        
        avail3 = G(AvailableInCountry, ingredient=sing, location=country,
                    transport_method=tpm, extra_production_footprint=100,
                    date_from=datetime.date(2013, 2, 2),
                    date_until=datetime.date(2013, 5, 1))
        self.assertEqual(sing.footprint(), avail3.footprint + 4*sing.preservation_footprint)
        
    
    def test_save(self):
        bing = G(Ingredient, type=Ingredient.BASIC, preservability=10,
                 preservation_footprint=100, base_footprint=1, accepted=True)
        self.assertEqual(bing.preservability, 0)
        self.assertEqual(bing.preservation_footprint, 0)
        
        # Check if recipe footprint is updated
        G(Cuisine, name='Andere')
        recipe = G(Recipe, portions=1)
        cuu = G(CanUseUnit, ingredient=bing, is_primary_unit=True, conversion_factor=1)
        G(UsesIngredient, recipe=recipe, ingredient=bing, amount=1, unit=cuu.unit)
        recipe.save()
        current_fp = recipe.footprint
        self.assertEqual(recipe.footprint, 1)
        
        bing.base_footprint = 10*bing.base_footprint
        bing.save()
        
        self.assertNotEqual(current_fp, Recipe.objects.get(id=recipe.id).footprint)
