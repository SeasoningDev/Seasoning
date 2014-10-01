# -*- coding: utf-8 -*- 
import time
import datetime
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import date as _date
from imagekit.models.fields import ProcessedImageField, ImageSpecField
from imagekit.processors.resize import ResizeToFill, SmartResize
from general import validate_image_size

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
    class Meta:
        db_table = 'unit'
        
    name = models.CharField(max_length=30L, unique=True)
    short_name = models.CharField(max_length=10L, blank=True)
    
    parent_unit = models.ForeignKey('self', related_name="derived_units", null=True, blank=True, limit_choices_to=models.Q(parent_unit__exact=None), default=None)
    ratio = models.FloatField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name
        
    def short(self):
        if self.short_name:
            return self.short_name
        return self.name
    
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
    
    useable_units = models.ManyToManyField(Unit, through='CanUseUnit')
    
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
        if self.pk == 273:
            ok = 1
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
                        # We started on jan 1st, if the next year has arrived, we're golden
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
    
class CanUseUnit(models.Model):
    """
    Relates a unit to an ingredient.
    
    The conversion factor defines how this unit relates to the ingredients primary unit in
    the following way:
        1 this_unit = conversion_factor primary_unit
    
    """    
    class Meta:
        db_table = 'canuseunit'
        
    ingredient = models.ForeignKey('Ingredient', db_column='ingredient')
    unit = models.ForeignKey('Unit', related_name='useable_by', db_column='unit', limit_choices_to=models.Q(parent_unit__exact=None))
    
    is_primary_unit = models.BooleanField(default=False)
    
    conversion_factor = models.FloatField()
    
    def __unicode__(self):
        return self.ingredient.name + ' can use ' + self.unit.name
    
    def save(self, *args, **kwargs):
        super(CanUseUnit, self).save(*args, **kwargs)
        if self.unit.parent_unit is None:
            for unit in self.unit.derived_units.all():
                try:
                    canuseunit = CanUseUnit.objects.get(ingredient=self.ingredient, unit=unit)
                    canuseunit.conversion_factor = self.conversion_factor*unit.ratio
                    canuseunit.save()
                except CanUseUnit.DoesNotExist:
                    CanUseUnit(ingredient=self.ingredient, unit=unit, is_primary_unit=False, conversion_factor=self.conversion_factor*unit.ratio).save()
    
    def delete(self, *args, **kwargs):
        super(CanUseUnit, self).delete(*args, **kwargs)
        if self.unit.parent_unit is None:
            # If this is a base unit, check if it has any derived canuseunits that need to be deleted
            for canuseunit in CanUseUnit.objects.filter(ingredient=self.ingredient, unit__parent_unit=self.unit):
                canuseunit.delete()
        

class Country(models.Model):
    """
    This class represent countries. Each country is a certain distance away from Belgium
    
    """
    class Meta:
        db_table = 'country'
    
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50L)
    distance = models.IntegerField()
    
    def __unicode__(self):
        return self.name


class Sea(models.Model):
    """
    Same as the ``Country`` model, but for fish ingredients
    
    """    
    class Meta:
        db_table = 'sea'
    
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50L)
    distance = models.IntegerField()
    
    def __unicode__(self):
        return self.name
    
class TransportMethod(models.Model):
    """
    This class represents a transport method. A transport method has a mean carbon emission
    per km
    
    """
    class Meta:
        db_table = 'transportmethod'
        
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20L)
    emission_per_km = models.FloatField()
    
    def __unicode__(self):
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
    DAYS_IN_BASE_YEAR = (datetime.date(BASE_YEAR, 12, 31) - datetime.date(BASE_YEAR - 1, 12, 31)).days
    
    class Meta:
        abstract = True
    
    # This field must be overriden by implementing models
    location = None
    
    transport_method = models.ForeignKey('Transportmethod', db_column='transport_method')
    
    production_type  = models.CharField(max_length=10, blank=True)
    extra_production_footprint = models.FloatField(default=0)
    
    date_from = models.DateField()
    date_until = models.DateField()
    
    def footprint(self, date=None):
        if date is None:
            date = datetime.date.today()
            
        footprint = self.extra_production_footprint + \
            self.location.distance*self.transport_method.emission_per_km
        
        if self.under_preservation(date):
            ok = self.days_preserving(date)
            footprint += self.days_preserving(date)*self.ingredient.preservation_footprint
        return footprint
    
    def full_footprint(self, date=None):
        """
        The total footprint for this ingredient provided by this AvailableIn
        
        """
        return self.ingredient.base_footprint + self.footprint(date)
    
    def full_date_until(self):
        """
        This function returns the end date of the period in which this AvailableIn
        was available.
        It takes into account the preservability period of its ingredient. If the 
        until date wraps around the year because of its preservability, the following 
        things take place:
         - The year of the returned date is reset to self.BASE_YEAR
         - If the date is bigger than self.date_from, the returned date is set to the 
           day before self.date_from
        
        """
        if self.ingredient.preservability > 0:
            extended_until_date = self.date_until + datetime.timedelta(days=self.ingredient.preservability)
            if self.date_until < self.date_from and extended_until_date > self.date_from:
                # extended until date overshot the from date, take the day before from date
                return (self.date_from - datetime.timedelta(days=1)).replace(year=self.BASE_YEAR)
            
            if extended_until_date.year > self.BASE_YEAR:
                # preservability pushed it over the edge
                days_in_next_year = (extended_until_date - datetime.date(self.BASE_YEAR, 12, 31)).days % 366
                extended_until_date = datetime.date(self.BASE_YEAR - 1, 12, 31) + datetime.timedelta(days=days_in_next_year)
                if extended_until_date > self.date_from:
                    # if we have a wraparound (mind jan 1st)
                    return (self.date_from - datetime.timedelta(days=1)).replace(year=self.BASE_YEAR)
            
            return extended_until_date
        return self.date_until
    
    def innie(self):
        # 2000      from          until  2001
        # |---------[-------------]------|
        return self.date_from < self.full_date_until()
    
    def outie(self):
        # 2000      until         from   2001
        # |---------]-------------[------|
        return self.date_from > self.full_date_until()
    
    def month_from(self):
        return _date(self.date_from, 'F')
    
    def month_until(self):
        return _date(self.date_until, 'F')
    
    def extended_month_until(self):
        return _date(self.full_date_until(), 'F')
    
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
            if date < self.date_from or self.full_date_until() < date:
                return False
            return True
        else:
            if self.full_date_until() < date and date < self.date_from:
                return False
            return True
    
    def under_preservation(self, date=None):
        """
        Returns if this available in is currently active. This means the
        ingredient can be supplied using these parameters today.
        
        """
        if date is None:
            date = datetime.date.today().replace(year=self.BASE_YEAR)
        else:
            date = date.replace(year=self.BASE_YEAR)
        
        if not self.is_active(date):
            return False
        
        """
        If its active, but not in the raw date_from to date_until period,
        it must be preserving
        
        """
        if self.innie():
            if date < self.date_from or self.date_until < date:
                return True
            return False
        else:
            if self.date_until < date or date < self.date_from:
                return True
            return False
    
    def days_preserving(self, date=None):
        if date is None:
            date = datetime.date.today().replace(year=self.BASE_YEAR)
        else:
            date = date.replace(year=self.BASE_YEAR)
        
        if not self.under_preservation(date):
            return 0
        
        if date > self.date_until:
            return (date - self.date_until).days
        
        return self.DAYS_IN_BASE_YEAR - (self.date_until - date).days
        
         
    def save(self, *args, **kwargs):
        self.date_from = self.date_from.replace(year=self.BASE_YEAR)
        self.date_until = self.date_until.replace(year=self.BASE_YEAR)
        
        super(AvailableIn, self).save(*args, **kwargs)
        
    
class AvailableInCountry(AvailableIn):
    """
    An implementation of the AvailableIn model for vegetal ingredients
    
    """
    class Meta:
        db_table = 'availableincountry'
    
    ingredient = models.ForeignKey(Ingredient, related_name='available_in_country', db_column='ingredient')
    location = models.ForeignKey('Country', db_column='country')
    
    def country(self):
        return self.location
    
class AvailableInSea(AvailableIn):
    """
    An implementation of the AvailableIn model for fish ingredients
    
    """    
    class Meta:
        db_table = 'availableinsea'
    
    ingredient = models.ForeignKey(Ingredient, related_name='available_in_sea', db_column='ingredient')
    location = models.ForeignKey('Sea', db_column='sea')
    
    endangered = models.BooleanField(default=False)
    
    def sea(self):
        return self.location
    
