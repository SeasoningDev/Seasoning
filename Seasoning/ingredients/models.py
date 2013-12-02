# -*- coding: utf-8 -*-
"""
Copyright 2012, 2013 Driesen Joep

This file is part of Seasoning.

Seasoning is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Seasoning is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Seasoning.  If not, see <http://www.gnu.org/licenses/>.
    
"""
from django.db import models
import time
from imagekit.models.fields import ProcessedImageField, ImageSpecField
from imagekit.processors.resize import ResizeToFill, SmartResize
import datetime
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import recipes
from django.utils.translation import ugettext_lazy as _

def get_image_filename(instance, old_filename):
    """
    Return a new unique filename for an ingredient image
    
    """
    filename = str(time.time()) + '.png'
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
    
    # Following ingredients are only used for Seasonal Ingredients
    # The amount of days an ingredient can be preserved
    preservability = models.IntegerField(default=0)
    preservation_footprint = models.FloatField(default=0)
    
    base_footprint = models.FloatField()
    
    image = ProcessedImageField(processors=[ResizeToFill(350, 350)], format='PNG', upload_to=get_image_filename, default='images/ingredients/no_image.png')
    thumbnail = ImageSpecField([SmartResize(220, 220)], image_field='image', format='PNG')
    
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
            if available_in.is_active(date, date_until_extension=self.preservability):
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
        
        smallest_footprint = None
        for available_in in self.get_active_available_ins(date):
            if self.name == 'Rode kool':
                x =1
            if not available_in.is_active(date_until_extension=0):
                # This means this available in is currently under preservation
                footprint = available_in.footprint + available_in.days_apart()*self.preservation_footprint
            else:
                footprint = available_in.footprint
            if not smallest_footprint or smallest_footprint > footprint:
                smallest_footprint = footprint
                smallest_available_in = available_in
        if smallest_footprint is None:
            raise ObjectDoesNotExist('No active AvailableIn object was found for ingredient ' + str(self))
        return smallest_available_in
        
    def always_available(self):
        """
        Check if this Ingredient is always available somewhere
        
        """
        try:
            available_ins = self.get_available_ins()
        except self.BasicIngredientException:
            return True
        
        current_date = datetime.date(AvailableIn.BASE_YEAR, 1, 1)
        
        while available_ins:
            before_loop_date = current_date
            for avail in available_ins:
                if avail.is_active(current_date, date_until_extension=self.preservability):
                    extended_until_date = avail.extended_date_until(date_until_extension=self.preservability)
                    if current_date < extended_until_date:
                        current_date = extended_until_date + datetime.timedelta(days=1)
                        if current_date.year > extended_until_date.year:
                            # We've wrapped around
                            return True                        
                    else:
                        # the availability wrapped around the year => we're finished
                        return True
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
            if not available_in.is_active(date_until_extension=0):
                # This means this available in is currently under preservation
                footprint = available_in.footprint + available_in.days_apart()*self.preservation_footprint
            else:
                footprint = available_in.footprint
            return footprint
        except self.BasicIngredientException:
            return self.base_footprint
    
    def can_use_unit(self, unit):
        return unit in self.useable_units.all()
    
    def clean(self):
        if self.accepted and not self.always_available():
            raise ValidationError(_('This ingredient is not always available somewhere, and should not be accepted.'))
        
    def save(self):
        if not self.type == Ingredient.SEASONAL:
            self.preservability = 0
            self.preservation_footprint = 0
        saved = super(Ingredient, self).save()
        
        # Update all recipes using this ingredient
        uses = recipes.models.UsesIngredient.objects.filter(ingredient=self)
        if len(uses) > 0 and len(uses) < 100:
            # If more than 100 recipes use this ingredient, just wait for the cron job to
            # avoid overloading the server
            for uses_ingredient in uses:
                uses_ingredient.save(update_recipe=True)
        
        return saved

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
    
    is_primary_unit = models.BooleanField()
    
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
    
    class Meta:
        abstract = True
    
    # This field must be overriden by implementing models
    location = None
    
    transport_method = models.ForeignKey('Transportmethod', db_column='transport_method')
    
    production_type  = models.CharField(max_length=10, blank=True)
    extra_production_footprint = models.FloatField(default=0)
    
    date_from = models.DateField()
    date_until = models.DateField()
    
    # This is the added footprint when an ingredient is available with this AvailableIn object,
    # it is calculated when the model is saved
    footprint = models.FloatField(editable=False)
    
    def extended_date_until(self, date_until_extension=None):
        if date_until_extension is None:
            date_until_extension = self.ingredient.preservability
        date = self.date_until + datetime.timedelta(days=date_until_extension)
        if date.year > self.BASE_YEAR:
            date = date.replace(year=self.BASE_YEAR)
            if date > self.date_from:
                return self.date_from
        return date
        
    def month_from(self):
        return self.date_from.strftime('%B')
    
    def month_until(self):
        return self.date_until.strftime('%B')
    
    def extended_month_until(self, date_until_extension=None):
        return self.extended_date_until(date_until_extension).strftime('%B')
    
    def is_active(self, date=None, date_until_extension=0):
        """
        Returns if this available in is currently active. This means the
        ingredient can be supplied using these parameters today.
        
        """
        if date is None:
            date = datetime.date.today().replace(year=self.BASE_YEAR)
        else:
            date = date.replace(year=self.BASE_YEAR)
        
        if date < self.date_from:
            date = date.replace(year=self.BASE_YEAR + 1)
            
        if self.date_from <= self.date_until:
            # 2000      from          until  2001
            # |---------[-------------]------|
            extended_until_date = (self.date_until + datetime.timedelta(days=date_until_extension))
        else:
            # 2000      until         from   2001
            # |---------]-------------[------|
            try:
                date_until = self.date_until.replace(year=self.BASE_YEAR + 1)
            except ValueError:
                if self.date_until.month == 2 and self.date_until.day == 29:
                    date_until = self.date_until.replace(day=28, year=self.BASE_YEAR + 1)
                else:
                    raise
            extended_until_date = (date_until + datetime.timedelta(days=date_until_extension))
            
        return date <= extended_until_date
    
    def save(self, *args, **kwargs):
        self.footprint = self.ingredient.base_footprint + self.extra_production_footprint + self.location.distance*self.transport_method.emission_per_km
        
        self.date_from = self.date_from.replace(year=self.BASE_YEAR)
        self.date_until = self.date_until.replace(year=self.BASE_YEAR)
        
        super(AvailableIn, self).save(*args, **kwargs)
    
    def days_apart(self, date=None):
        """
        Returns the amount of days between the date_until of this available in object
        and the given date.
        If the given date is between date_from and date_until, 0 is returned
        
        """
        if date is None:
            date = datetime.date.today().replace(year=self.BASE_YEAR)
        else:
            date = date.replace(year=self.BASE_YEAR)
        
        if self.is_active(date):
            return 0
        
        if date < self.date_until:
            date = date.replace(year=self.BASE_YEAR + 1)
        
        return (date - self.date_until).total_seconds() // (24*60*60)
    

    
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
    
    endangered = models.BooleanField()
    
    def sea(self):
        return self.location
    
