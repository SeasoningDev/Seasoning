# -*- coding: utf-8 -*- 
import time
from django.db import models
from imagekit.models.fields import ProcessedImageField, ImageSpecField
from imagekit.processors.resize import ResizeToFill, SmartResize
import datetime
import re

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
    
    def name_needed(self):
        return 'stuk' not in self.name.lower()
    
    def get_display_name(self):
        if self.name_needed():
            m = re.match('(.*)\(.*\)', self.name)
            if m:
                return m.group(1)
            
            return self.name
        
        return ''
    
    def get_display_name_plural(self):
        if self.name_needed():
            return self.name.replace('(', '').replace(')', '')
        
        return ''
    
    

class IngredientManager(models.Manager):
    
    def accepted(self):
        return self.filter(accepted=True)
    
class Ingredient(models.Model):
    """
    This is the base class for ingredients. It is not an abstract class, as simple
    Ingredients can be represented by it. This includes meat, which is not 
    dependent on time and has no special attributes
    
    """
    class Meta:
        ordering = ('name', )
    
    class BasicIngredientException(Exception):
        pass
    
    objects = IngredientManager()
    
    
    
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
    
    def can_use_unit(self, unit):
        unit = unit.parent_unit or unit
        
        if unit in self.useable_units.all():
            return True
        
        return False
        
    
    
    ACTIVE, PRESERVING, INACTIVE = 0, 1, 2
    def get_available_ins_sorted_by_footprint(self, date=None):
        if self.type is self.BASIC:
            return []
        
        elif self.type is self.SEASONAL:
            availables = self.available_in_country.all()
            
        elif self.type is self.SEASONAL_SEA:
            availables = self.available_in_sea.all()
        
        availables_fp = []
        for available in availables:
            availables_fp.append({'available_in_object': available, 
                                  'state': self.ACTIVE, 
                                  'transportation_footprint': available.transportation_footprint(),
                                  'production_footprint': available.extra_production_footprint,
                                  'current_footprint': available.total_extra_footprint()})
            
            if not available.is_active(date):
                availables_fp[-1]['preservation_footprint'] = available.days_since_last_active(date) * self.preservation_footprint 
                availables_fp[-1]['current_footprint'] += availables_fp[-1]['preservation_footprint']
                
                if self.preservability < available.days_since_last_active(date):
                    availables_fp[-1]['state'] = self.INACTIVE
                
                else:
                    availables_fp[-1]['state'] = self.PRESERVING
                    
        return sorted(availables_fp, key=lambda avail: avail['current_footprint'])
    
    def get_useable_available_in_with_lowest_footprint(self, date=None):
        for avail in self.get_available_ins_sorted_by_footprint(date):
            if avail['state'] is not self.INACTIVE:
                return avail
        
        raise Exception('No available in object is currently active')
            
    def is_in_season(self, date=None):
        try:
            return self.get_available_ins_sorted_by_footprint(date)[0]['state'] is not self.INACTIVE
        
        except IndexError:
            return True
        
    
    
    def footprint(self, date=None):
        if self.type is self.BASIC:
            return self.base_footprint
        
        avail = self.get_useable_available_in_with_lowest_footprint(date)
        return self.base_footprint + avail['current_footprint']
    
    def footprint_breakdown(self, date=None):
        breakdown = {'Base Footprint': self.base_footprint}
        
        if self.type is self.BASIC:
            breakdown.update({'Production': 0,
                              'Transportation': 0,
                              'Preservation': 0})
        
        else:
            avail = self.get_useable_available_in_with_lowest_footprint(date)
            
            breakdown.update({'Production': avail['production_footprint'],
                              'Transportation': avail['transportation_footprint'],
                              'Preservation': avail.get('preservation_footprint', 0)})
                         
        return breakdown
        
        
        
    
    
    
    def is_endangered(self, date=None):
        if self.type is not self.SEASONAL_SEA:
            return False
        
        return self.get_available_ins_sorted_by_footprint(date)[0]['available_in_object'].endangered 
        
            

class Synonym(models.Model):
    """
    Represents a synonym for an ingredient, these will be displayed when viewing
    ingredients, and can be searched for.
    
    """
    name = models.CharField(max_length=50, unique=True)
    plural_name = models.CharField(max_length=50, blank=True)
    
    ingredient = models.ForeignKey(Ingredient, related_name='synonyms', null=True, blank=True)
    
    def __str__(self):
        return '{} (synonym of ingredient {})'.format(self.name, self.ingredient_id)
    
    
    
class CanUseUnit(models.Model):
    """
    Relates a unit to an ingredient.
    
    The conversion factor defines how this unit relates to the ingredients primary unit in
    the following way:
        1 this_unit = conversion_factor primary_unit
    
    """    
    ingredient = models.ForeignKey('Ingredient', related_name='can_use_units')
    unit = models.ForeignKey('Unit', related_name='useable_by', limit_choices_to=models.Q(parent_unit__isnull=True))
    
    conversion_ratio = models.FloatField()
    
    def __str__(self):
        return 'Ingredient {} can use unit {}'.format(self.ingredient_id, self.unit_id)
    
        

class Country(models.Model):
    """
    This class represent countries. Each country is a certain distance away from Belgium
    
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    distance = models.IntegerField()
    
    def __str__(self):
        return self.name

class Sea(models.Model):
    """
    Same as the ``Country`` model, but for fish ingredients
    
    """    
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    distance = models.IntegerField()
    
    def __str__(self):
        return self.name
    
    
    
class TransportMethod(models.Model):
    """
    This class represents a transport method. A transport method has a mean carbon emission
    per km
    
    """
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    emissions_per_km = models.FloatField()
    
    def __str__(self):
        return self.name
    
    
    
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
    
    
    
    def innie(self):
        # 2000      from          until  2001
        # |---------[-------------]------|
        return self.date_from < self.date_until
    
    def outie(self):
        # 2000      until         from   2001
        # |---------]-------------[------|
        return self.date_from > self.date_until
    
    def is_active(self, date=None):
        """
        Returns if this available in is currently active. This means the
        ingredient can be supplied using these parameters today.
        
        """
        if date is None:
            date = datetime.date.today().replace(year=self.BASE_YEAR)
        else:
            date = date.replace(year=self.BASE_YEAR)
        
        if self.innie():
            if date < self.date_from or self.date_until < date:
                return False
            return True
        else:
            if self.date_until < date and date < self.date_from:
                return False
            return True
    
    def days_since_last_active(self, date=None):
        if date is None:
            date = datetime.date.today().replace(year=self.BASE_YEAR)
        else:
            date = date.replace(year=self.BASE_YEAR)
        
        if self.is_active(date):
            return 0
        
        if date < self.date_until:
            date = date.replace(year=self.BASE_YEAR + 1)
        
        return (date - self.date_until).days
    
        
    
    def transportation_footprint(self):
        return self.location.distance * self.transport_method.emissions_per_km
    
    def total_extra_footprint(self):
        return self.transportation_footprint() + self.extra_production_footprint
    
    
    
    def save(self, force_insert=False, force_update=False, using=None, 
        update_fields=None):
        
        self.date_from = self.date_from.replace(year=self.BASE_YEAR)
        self.date_until = self.date_until.replace(year=self.BASE_YEAR)
        
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
    
class AvailableInCountry(AvailableIn):
    """
    An implementation of the AvailableIn model for vegetal ingredients
    
    """
    ingredient = models.ForeignKey(Ingredient, related_name='available_in_country')
    location = models.ForeignKey('Country')
    
    def __str__(self):
        return 'Ingredient {} is available in Country {}'.format(self.ingredient_id, self.location_id)
    
class AvailableInSea(AvailableIn):
    """
    An implementation of the AvailableIn model for fish ingredients
    
    """    
    ingredient = models.ForeignKey(Ingredient, related_name='available_in_sea')
    location = models.ForeignKey('Sea')
    
    endangered = models.BooleanField()
    
    def __str__(self):
        return 'Ingredient {} is available in Sea {}'.format(self.ingredient_id, self.location_id)
