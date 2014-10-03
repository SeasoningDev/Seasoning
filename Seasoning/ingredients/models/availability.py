from django.db import models
from django.template.defaultfilters import date as _date
import datetime

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
        
    def footprint(self, date=None):
        if date is None:
            date = datetime.date.today()
            
        footprint = self.extra_production_footprint + \
            self.location.distance*self.transport_method.emission_per_km
        
        if self.under_preservation(date):
            footprint += self.days_preserving(date)*self.ingredient.preservation_footprint
        return footprint
    
    def full_footprint(self, date=None):
        """
        The total footprint for this ingredient provided by this AvailableIn
        
        """
        return self.ingredient.base_footprint + self.footprint(date)
    
         
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
    
    ingredient = models.ForeignKey('Ingredient', related_name='available_in_country', db_column='ingredient')
    location = models.ForeignKey('Country', db_column='country')
    
    def country(self):
        return self.location
    
class AvailableInSea(AvailableIn):
    """
    An implementation of the AvailableIn model for fish ingredients
    
    """    
    class Meta:
        db_table = 'availableinsea'
    
    ingredient = models.ForeignKey('Ingredient', related_name='available_in_sea', db_column='ingredient')
    location = models.ForeignKey('Sea', db_column='sea')
    
    endangered = models.BooleanField(default=False)
    
    def sea(self):
        return self.location
