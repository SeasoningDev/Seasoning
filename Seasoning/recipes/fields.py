from django import forms
from ingredients.models.units import Unit
from django.core.exceptions import ValidationError

        
class MultipleSeparatorsFloatField(forms.FloatField):
    """
    A float field that allows both '.' and ',' as decimal separators
    
    """
    def clean(self, value):
        value = value.replace(',', '.')
        return super(MultipleSeparatorsFloatField, self).clean(value)
    
class ChooseRealDisplayTempUnitField(forms.ModelChoiceField):
    
    """
    This is a cache to reduce database hits in formset. It will require a server restart
    when new units are added for them to show up (not often)
    
    """
    unit_choices = [(unit.id, unit.name) for unit in Unit.objects.all()]
    
    def __init__(self, *args, **kwargs):
        result = super(ChooseRealDisplayTempUnitField, self).__init__(queryset=Unit.objects, *args, **kwargs)
        self.choices = [(None, self.empty_label)]
        self.choices.extend(self.unit_choices)
        return result
    
    def clean(self, *args, **kwargs):
        try:
            result = super(ChooseRealDisplayTempUnitField, self).clean(*args, **kwargs)
        except ValidationError as e:
            if e.message == self.error_messages['required']:
                result = None
            else:
                raise e
        return result