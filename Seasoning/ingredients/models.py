# -*- coding: utf-8 -*- 
import time
from django.db import models
from imagekit.models.fields import ProcessedImageField, ImageSpecField
from imagekit.processors.resize import ResizeToFill, SmartResize

def get_image_filename(instance, old_filename):
    """
    Return a new unique filename for an ingredient image
    
    """
    extension = old_filename.split('.')[-1]
    filename = '%s.%s' % (str(time.time()), extension)
    return 'images/ingredients/' + filename

class Unit(models.Model):
    """
    Represent a unit
    
    A unit can be dependent on a parent unit. This means that the
    ratio between these units is independent of the ingredient.
    
    If a unit does has a parent unit, it cannot be selected as a
    unit useable by any ingredient. It will, however, automatically
    be available to any ingredient that can use its parent unit
    
    A unit with a parent unit can itself not be used as a parent unit,
    to prevent infinite recursion and other nasty stuff
    
    The ratio is defined as follows:
        1 this_unit = ratio parent_unit
    
    """
    name = models.CharField(max_length=30, unique=True)
    short_name = models.CharField(max_length=10, blank=True)
    
    parent_unit = models.ForeignKey('self', related_name="derived_units", null=True, blank=True, limit_choices_to=models.Q(parent_unit__exact=None), default=None)
    ratio = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    

class Ingredient(models.Model):
    """
    This is the base class for ingredients. It is not an abstract class, as simple
    Ingredients can be represented by it. This includes meat, which is not 
    dependent on time and has no special attributes
    
    """
    
    class BasicIngredientException(Exception):
        pass
    
    # Choices
    DRINKS, FRUIT, CEREAL, VEGETABLES, HERBS_AND_SPICES, NUTS_AND_SEEDS, OILS, LEGUME, SEAFOOD, SUPPLEMENTS, FISH, MEAT, MEAT_SUBS, DAIRY_PRODUCTS = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
    CATEGORIES = ((DRINKS,u'Dranken'),
                  (FRUIT,u'Fruit'),
                  (CEREAL,u'Graanproducten'),
                  (VEGETABLES,u'Groenten'),
                  (HERBS_AND_SPICES,u'Kruiden en specerijen'),
                  (NUTS_AND_SEEDS,u'Noten en zaden'),
                  (OILS,u'Oliën'),
                  (LEGUME,u'Peulvruchten'),
                  (SEAFOOD,u'Schaal- en schelpdieren'),
                  (SUPPLEMENTS,u'Supplementen'),
                  (FISH,u'Vis'),
                  (MEAT,u'Vlees'),
                  (MEAT_SUBS,u'Vleesvervangers'),
                  (DAIRY_PRODUCTS,u'Zuivel'))
    NON_VEGETARIAN, VEGETARIAN, VEGAN  = 0, 1, 2
    VEGANISMS = ((VEGAN,u'Veganistisch'),
                 (VEGETARIAN,u'Vegetarisch'),
                 (NON_VEGETARIAN,u'Niet-Vegetarisch'))
    BASIC, SEASONAL, SEASONAL_SEA = 0, 1, 2
    TYPES = ((BASIC, u'Basis'),
             (SEASONAL, u'Seizoensgebonden'),
             (SEASONAL_SEA,  u'Seizoensgebonden Zee'))
    
    name = models.CharField(max_length=50, unique=True)
    plural_name = models.CharField(max_length=50, blank=True)
    
    type = models.PositiveSmallIntegerField(choices=TYPES, default=BASIC)
    
    category = models.PositiveSmallIntegerField(choices=CATEGORIES)
    veganism = models.PositiveSmallIntegerField(choices=VEGANISMS, default=VEGAN)
    
    description = models.TextField(blank=True)
    conservation_tip = models.TextField(blank=True)
    preparation_tip = models.TextField(blank=True)
    properties = models.TextField(blank=True)
    source = models.TextField(blank=True)
    
    # Following fields are only used for Seasonal Ingredients
    # The amount of days an ingredient can be preserved
    preservability = models.IntegerField(default=0)
    preservation_footprint = models.FloatField(default=0)
    
    base_footprint = models.FloatField()
    
    image = ProcessedImageField(format='JPEG', processors=[ResizeToFill(350, 350)], upload_to=get_image_filename, default='images/no_image.jpg')
    thumbnail = ImageSpecField([SmartResize(220, 220)], source='image', format='JPEG')
    image_source = models.TextField(blank=True)
    
    accepted = models.BooleanField(default=False)
    bramified = models.BooleanField(default=False)
    
    useable_units = models.ManyToManyField(Unit, through='CanUseUnit')
    
    def __str__(self):
        return self.name
    
    def footprint(self):
        if self.type is self.BASIC:
            return self.base_footprint
        
        elif self.type is self.SEASONAL:
            availables = self.available_in_country.all()
            
        elif self.type is self.SEASONAL_SEA:
            availables = self.available_in_sea.all()
        
            
        min_extra_footprint = None
        if len(availables) <= 0:
            raise Exception(self.get_type_display())
        for available in availables:
            if min_extra_footprint is None or available.total_extra_footprint() < min_extra_footprint:
                min_extra_footprint = available.total_extra_footprint()
        
        return self.base_footprint + min_extra_footprint
        
        
            

class Synonym(models.Model):
    """
    Represents a synonym for an ingredient, these will be displayed when viewing
    ingredients, and can be searched for.
    
    """
    name = models.CharField(max_length=50, unique=True)
    plural_name = models.CharField(max_length=50, blank=True)
    
    ingredient = models.ForeignKey(Ingredient, related_name='synonyms', null=True, blank=True)
    
    
    
class CanUseUnit(models.Model):
    """
    Relates a unit to an ingredient.
    
    The conversion factor defines how this unit relates to the ingredients primary unit in
    the following way:
        1 this_unit = conversion_factor primary_unit
    
    """    
    ingredient = models.ForeignKey('Ingredient')
    unit = models.ForeignKey('Unit', related_name='useable_by', limit_choices_to=models.Q(parent_unit__isnull=True))
    
    conversion_ratio = models.FloatField()
    
        

class Country(models.Model):
    """
    This class represent countries. Each country is a certain distance away from Belgium
    
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    distance = models.IntegerField()

class Sea(models.Model):
    """
    Same as the ``Country`` model, but for fish ingredients
    
    """    
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    distance = models.IntegerField()
    
    
    
class TransportMethod(models.Model):
    """
    This class represents a transport method. A transport method has a mean carbon emission
    per km
    
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    emission_per_km = models.FloatField()
    
    
    
class AvailableIn(models.Model):
    """
    Seasonal ingredients are available in different parts of the world at
    different time. Their footprint depends on where they come from.
    
    This model expresses where a seasonal ingredient can come from between
    certain times of the year, how it is transported to Belgium and what the
    additional footprint is during the production in this location (eg. because of
    greenhouse production)
    
    """
    BASE_YEAR = 2000
    
    class Meta:
        abstract = True
    
    # This field must be overriden by implementing models
    location = None
    
    transport_method = models.ForeignKey('Transportmethod')
    
    production_type  = models.CharField(max_length=10, blank=True)
    extra_production_footprint = models.FloatField(default=0)
    
    date_from = models.DateField()
    date_until = models.DateField()
    
    def transportation_footprint(self):
        return self.location.distance * self.transport_method.emission_per_km
    
    def total_extra_footprint(self):
        return self.transportation_footprint() + self.extra_production_footprint
    
class AvailableInCountry(AvailableIn):
    """
    An implementation of the AvailableIn model for vegetal ingredients
    
    """
    ingredient = models.ForeignKey(Ingredient, related_name='available_in_country')
    location = models.ForeignKey('Country')
    
class AvailableInSea(AvailableIn):
    """
    An implementation of the AvailableIn model for fish ingredients
    
    """    
    ingredient = models.ForeignKey(Ingredient, related_name='available_in_sea')
    location = models.ForeignKey('Sea')
    
    endangered = models.BooleanField()
