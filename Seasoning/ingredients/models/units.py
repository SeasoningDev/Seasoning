from django.db import models

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
    
    def singular_name(self):
        if '(' in self.name:
            return self.name.split('(')[0]
        return self.name

    def plural_name(self):
        if '(' not in self.name:
            return self.name
        return self.name.replace('(', '').replace(')', '')
    
    def name_needed(self):
        return not 'stuk' in self.name
        
    def short(self, plural=False):
        if self.short_name and not self.name == self.short_name:
            return self.short_name
        
        if plural:
            return self.plural_name()
        return self.singular_name()
    
    def short_plural(self):
        return self.short(True)
    
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
        """
        If this objects unit has derived units, make CanUseUnit objects for each of these
        derived units
        
        """
        super(CanUseUnit, self).save(*args, **kwargs)
        
        if self.unit.parent_unit is None:
            # This is a base unit, create CanUseUnit objects for each of its derived units
            for unit in self.unit.derived_units.all():
                try:
                    # Check if the required CanUseUnit objects already exists, and if so, update it
                    canuseunit = CanUseUnit.objects.get(ingredient=self.ingredient, unit=unit)
                    canuseunit.conversion_factor = self.conversion_factor*unit.ratio
                    canuseunit.save()
                except CanUseUnit.DoesNotExist:
                    # Create a new CanUseUnit object
                    CanUseUnit(ingredient=self.ingredient, unit=unit, is_primary_unit=False, conversion_factor=self.conversion_factor*unit.ratio).save()
    
    def delete(self, hard_delete=False):
        """
        If a CanUseUnit is deleted, we should also delete all the CanUseUnits that use
        a unit to which this CanUseUnits unit can be converted
        
        """
        if hard_delete:
            return super(CanUseUnit, self).delete()
            
        if self.unit.parent_unit is None:
            # If this is a base unit, check if it has any derived canuseunits that need to be deleted
            for canuseunit in CanUseUnit.objects.filter(ingredient=self.ingredient, unit__parent_unit=self.unit):
                canuseunit.delete(hard_delete=True)
            # Delete self
            self.delete(hard_delete=True)
        else:
            # This is a derived unit, delete its parent canuseunit to remove all convertible canuseunits
            try:
                parent_canuseunit = CanUseUnit.objects.get(ingredient=self.ingredient, unit=self.unit.parent_unit)
                parent_canuseunit.delete()
            except CanUseUnit.DoesNotExist:
                # If no parent objects exist, just delete this canuseunit
                self.delete(hard_delete=True)
            