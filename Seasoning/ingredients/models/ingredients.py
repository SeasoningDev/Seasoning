# -*- coding: utf-8 -*-
from django.db import models
import datetime
from imagekit.models.fields import ImageSpecField, ProcessedImageField
from imagekit.processors.resize import ResizeToFill, SmartResize
from general import validate_image_size
from units import CanUseUnit
from django.core.exceptions import ObjectDoesNotExist
from availability import AvailableIn
import time

def get_image_filename(instance, old_filename):
    """
    Return a new unique filename for an ingredient image
    
    """
    extension = old_filename.split('.')[-1]
    filename = '%s.%s' % (str(time.time()), extension)
    return 'images/ingredients/' + filename

class IngredientManager(models.Manager):
    
    def with_name(self, name):
        name_filter = models.Q(name__iexact=name) | models.Q(synonyms__name__iexact=name)
        return self.distinct().get(name_filter)
    
    def accepted_with_name(self, name):
        name_filter = models.Q(name__iexact=name) | models.Q(synonyms__name__iexact=name)
        return self.distinct().get(name_filter, accepted=True)
    
    def with_name_like(self, name):
        name_filter = models.Q(name__icontains=name) | models.Q(synonyms__name__icontains=name)
        return self.distinct().filter(name_filter)
    
    def accepted_with_name_like(self, name):
        name_filter = models.Q(name__icontains=name) | models.Q(synonyms__name__icontains=name)
        return self.distinct().filter(name_filter, accepted=True)

class Ingredient(models.Model):
    """
    This is the base class for ingredients. It is not an abstract class, as simple
    Ingredients can be represented by it. This includes meat, which is not 
    dependent on time and has no special attributes
    
    """
    class Meta:
        db_table = 'ingredient'
    
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
    
    name = models.CharField(max_length=50L, unique=True)
    plural_name = models.CharField(max_length=50L, blank=True)
    
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
    
    image = ProcessedImageField(format='JPEG', processors=[ResizeToFill(350, 350)], upload_to=get_image_filename, 
                                validators=[validate_image_size], default='images/no_image.jpg')
    thumbnail = ImageSpecField([SmartResize(220, 220)], image_field='image', format='JPEG')
    image_source = models.TextField(blank=True)
    
    accepted = models.BooleanField(default=False)
    bramified = models.BooleanField(default=False)
    
    useable_units = models.ManyToManyField('Unit', through='CanUseUnit')
    
    def __unicode__(self):
        return self.name

    @property
    def primary_unit(self):
        try:
            useable_units = self.canuseunit_set.all()
            for useable_unit in useable_units:
                if useable_unit.is_primary_unit:
                    return useable_unit.unit
            return None
        except CanUseUnit.DoesNotExist:
            return None
    
    def months_preservable(self):
        return self.preservability // 30
    
    def preservation_footprint_monthly(self):
        return self.preservation_footprint * 30
    
    def get_available_ins(self):
        """
        Returns a queryset for all the available in objects belonging to this ingredient
        
        """
        if self.type == Ingredient.BASIC:
            raise self.BasicIngredientException
        elif self.type == Ingredient.SEASONAL:
            return self.available_in_country.all()
        elif self.type == Ingredient.SEASONAL_SEA:
            return self.available_in_sea.all()
    
    def get_available_ins_sorted(self):
        return sorted(self.get_available_ins(), key=lambda available_in: available_in.footprint())
    
    def get_active_available_ins(self, date=None):
        """
        Returns a list of the available in objects belonging to this ingredient
        that are available on the given date (The given date is between the from and until
        date). If no date is given, the current date will be used
        
        The until date is extended with the preservability of the ingredient
        
        This is done natively instead of through SQL because the SQL query would be 
        pretty complicated, while the performance benefit is not very obvious as
        every ingredient will only have a few available_ins
        
        """
        if date is None:
            date = datetime.date.today()
            
        active_available_ins = []
        for available_in in self.get_available_ins():
            if available_in.is_active(date):
                active_available_ins.append(available_in)
        return active_available_ins
    
    def get_available_in_with_smallest_footprint(self, date=None):
        """
        Return the AvailableIn with the smallest footprint of the AvailableIn objects 
        that are active on the given date beloning to this ingredient. If no date
        is given, the current date will be assumed
        
        If this is a basic ingredient, the footprint is just the base_footprint of the
        object
        
        If this is a Seasonal ingredient, the footprint is the base_footprint of the
        object, plus the minimal of the currently available AvailableIn* objects.
        
        """
        if date is None:
            date = datetime.date.today()
        
        active_available_ins = self.get_active_available_ins(date)
        sorted_active_availeble_ins = sorted(active_available_ins, key=lambda x: x.footprint(date))
        try:
            return sorted_active_availeble_ins[0]
        except IndexError:
            raise ObjectDoesNotExist('No active AvailableIn object was found for ingredient ' + str(self))
        
    def always_available(self):
        """
        Check if this Ingredient is always available somewhere
        
        """
        try:
            available_ins = self.get_available_ins()
        except self.BasicIngredientException:
            return True
        
        # All dates before this date (in the base year) the ingredient is sure to be available
        current_date = datetime.date(AvailableIn.BASE_YEAR, 1, 1)
        
        while available_ins:
            before_loop_date = current_date
            
            # Find an available in that is currently active
            for avail in available_ins:
                # Found an active available in
                if avail.is_active(current_date):
                    
                    if avail.outie():
                        if current_date > avail.date_from:
                            # |------]---------------[-----------x---------------|
                            # 2000   date_until      date_from   current_date    2001
                            # -> This means we are done
                            return True
                    
                    # The end date of this available in with preservability
                    extended_until_date = avail.full_date_until()
                    
                    # Add a day to include dates that end the day before the start date => these are valid as well
                    extended_until_date += datetime.timedelta(days=1)
                    
                    if extended_until_date.year > AvailableIn.BASE_YEAR:
                        # We started on jan 1st, if the next year has arrivxed, we're golden
                        return True
                        
                    current_date = extended_until_date
                    
            if before_loop_date == current_date:
                # This loop did nothing
                return False        
    
    def footprint(self, date=None):
        """
        Return the (minimal available) footprint of this ingredient on the given date.
        If no date is given, the current date will be assumed.
        
        If this is a basic ingredient, the footprint is just the base_footprint of the
        object
        
        If this is a Seasonal ingredient, the footprint is the base_footprint of the
        object, plus the minimal of the currently available AvailableIn* objects.
        
        """
        if date is None:
            date = datetime.date.today()
        
        try:
            available_in = self.get_available_in_with_smallest_footprint(date)
            return available_in.full_footprint(date)
        except self.BasicIngredientException:
            return self.base_footprint
    
    def coming_from_endangered(self):
        if self.type == Ingredient.SEASONAL_SEA:
            for available_in in self.get_active_available_ins():
                if available_in.endangered:
                    return True
        return False
    
    def can_use_unit(self, unit):
        return unit in self.useable_units.all()
    
    def save(self, *args, **kwargs):
        if not self.type == Ingredient.SEASONAL:
            self.preservability = 0
            self.preservation_footprint = 0
            
        return super(Ingredient, self).save()
        
class Synonym(models.Model):
    """
    Represents a synonym for an ingredient, these will be displayed when viewing
    ingredients, and can be searched for.
    
    """    
    class Meta:
        db_table = 'synonym'
    
    name = models.CharField(max_length=50L, unique=True)
    plural_name = models.CharField(max_length=50L, blank=True)
    
    ingredient = models.ForeignKey(Ingredient, related_name='synonyms', null=True, db_column='ingredient', blank=True)
    
    def __unicode__(self):
        return self.name
    