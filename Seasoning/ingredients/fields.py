# Based on django-ajax-selects from crucialfelix
import datetime
import calendar
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms.widgets import Widget, Select
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from ingredients.models import Ingredient

class MonthWidget(Widget):
        
    month_field = '%s_month'
    
    def render(self, name, value, attrs=None):
        try:
            month_val = value.month
        except AttributeError:
            try:
                month_val = datetime.datetime.strptime(value, '%Y-%m-%d').month
            except TypeError:
                month_val = None
        
        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        month_choices = ((0, '---'),
                         (1, 'Januari'), (2, 'Februari'), (3, 'Maart'), (4, 'April'), (5, 'Mei'), (6, 'Juni'),
                         (7, 'Juli'), (8, 'Augustus'), (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'December'))
        local_attrs = self.build_attrs(id=self.month_field % id_)
        s = Select(choices=month_choices)
        select_html = s.render(self.month_field % name, month_val, local_attrs)
        output.append(select_html)
        
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        m = int(data.get(self.month_field % name))
        if m == 0:
            return None
        if m:
            return '%d-%02d-%02d' % (2000, m, 1)
        return data.get(name, None)

class LastOfMonthWidget(MonthWidget):
    def value_from_datadict(self, data, files, name):
        m = int(data.get(self.month_field % name))
        if m == 0:
            return None
        if m:
            return '%d-%02d-%02d' % (2000, m, calendar.monthrange(2000, int(m))[1])
        return data.get(name, None)
    
class AutoCompleteSelectIngredientWidget(forms.widgets.HiddenInput):
    
    text_input = forms.widgets.TextInput(attrs={'placeholder': 'Zoek Ingredienten', 'class': 'keywords-searchbar'})

    def render(self, name, value, attrs={}):
        """
        We render this field as a hidden id input field and a text input field
        
        If the id is given, the text field should be filled in with the name of the
        corresponding ingredient
        
        """
        attrs['class'] = '{} ingredient-id-input'.format(attrs.get('class', ''))
        id_input_html = super(AutoCompleteSelectIngredientWidget, self).render(name, value, attrs)
        
        try:
            ingredient_name = Ingredient.objects.get(id=value)
        except Ingredient.DoesNotExist:
            ingredient_name = ''
        
        text_input_name = '{}-text'.format(name)
        text_input_html = self.text_input.render(text_input_name, ingredient_name, {'id': 'id_{}'.format(text_input_name)})
        
        return text_input_html + id_input_html
        
    
class AutoCompleteSelectIngredientField(forms.ModelChoiceField):
    """
    Form field that shows a text input in which the name of the ingredient
    should be typed and a hidden text input that should hold the id of the
    ingredient or no value if it represents an ingredient not present in
    the database.
    
    """
    
    def __init__(self, queryset=None, empty_label="---------", cache_choices=False, 
                       required=True, widget=None, label=None, initial=None, 
                       help_text='', to_field_name=None, limit_choices_to=None, *args, **kwargs):
        
        if queryset is None:
            queryset = Ingredient.objects.all()
        
        if widget is None:
            widget = AutoCompleteSelectIngredientWidget()
            
        super(AutoCompleteSelectIngredientField, self).__init__(queryset, empty_label, cache_choices,
                                                                required, widget, label, initial, 
                                                                help_text, to_field_name, limit_choices_to,
                                                                *args, **kwargs)
    
    def clean(self, value):
        if value == '':
            return Ingredient.objects.dummy()
        return super(AutoCompleteSelectIngredientField, self).clean(value)
    