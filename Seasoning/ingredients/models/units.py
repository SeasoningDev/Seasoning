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
        
    def short(self):
        if self.short_name:
            return self.short_name
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
