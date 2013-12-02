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
# Based on django-ajax-selects from crucialfelix
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from ingredients.models import Ingredient
from django.forms.widgets import Widget, Select
from django.utils.safestring import mark_safe
import calendar
from django.core.exceptions import ValidationError
from django.db import models
import datetime

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
    
class AutoCompleteSelectIngredientWidget(forms.widgets.TextInput):

    def render(self, name, value, attrs=None):
        value = value or ''
        if value:
            try:
                ingredient_pk = int(value)
                value = Ingredient.objects.get(pk=ingredient_pk).name
            except ValueError:
                # If we cannot cast the value into an int, it's probably the name of
                # the ingredient already, so we don't need to do anything
                pass
            except ObjectDoesNotExist:
                raise Exception("Cannot find ingredient with id: %s" % value)
        return super(AutoCompleteSelectIngredientWidget, self).render(name, value, attrs)
    
class AutoCompleteSelectIngredientField(forms.fields.CharField):

    """
    Form field to select a model for a ForeignKey db field
    """
    
    unknown_ingredient_error_message = 'The given ingredient was not found.'
    
    def __init__(self, *args, **kwargs):
        widget = kwargs.get('widget', False)
        if not widget or not isinstance(widget, AutoCompleteSelectIngredientWidget):
            kwargs['widget'] = AutoCompleteSelectIngredientWidget(attrs={'placeholder': 'Zoek Ingredienten', 'class': 'keywords-searchbar'})
        self.unaccepted_ingredients_allowed = kwargs.pop('unaccepted_ingredients_allowed', False)
        super(AutoCompleteSelectIngredientField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(AutoCompleteSelectIngredientField, self).to_python(value)
        if value == '':
            # If the field is not filled in, the parent class will do the validation
            return value
        try:
            if self.unaccepted_ingredients_allowed:
                ingredient = Ingredient.objects.with_name(value)
            else:
                ingredient = Ingredient.objects.accepted_with_name(value)
        except (ValueError, Ingredient.DoesNotExist):
            raise ValidationError(self.unknown_ingredient_error_message)
        return ingredient
            