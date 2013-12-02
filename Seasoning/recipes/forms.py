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
from django import forms
from recipes.models import Recipe, UsesIngredient, Cuisine
import recipes
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from ingredients.fields import AutoCompleteSelectIngredientField
from ingredients.models import Ingredient, Unit
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.core.exceptions import ValidationError
from markitup.widgets import MarkItUpWidget
from general.forms import FormContainer
from django.forms.util import ErrorDict

class AddRecipeForm(forms.ModelForm):
    
    class Meta:
        model = Recipe
        exclude = ['author', 'time_added',
                   'rating', 'number_of_votes',
                   'thumbnail', 'accepted']
    
    class Media:
        css = {
            'all': ('css/forms.css',)
        }
        
#    instructions = forms.CharField(widget=WMDWidget())
    
    def save(self, author, commit=True):
        recipe = super(AddRecipeForm, self).save(commit=False)
        recipe.author = author
        return recipe.save()

class EditRecipeBasicInfoForm(forms.ModelForm):
    
    class Meta:
        model = Recipe
        fields = ['name', 'course', 'cuisine',
                  'description', 'image']
    
    class Media:
        css = {
            'all': ('css/forms.css',)
        }

class EditRecipeIngredientInfoForm(forms.ModelForm):
    
    class Meta:
        model = Recipe
        fields = ['portions', 'extra_info']
    
    class Media:
        css = {
            'all': ('css/forms.css',)
        }
    
    request_unknown_ingredients = forms.BooleanField(required=False)

class UsesIngredientForm(forms.ModelForm):    
    class Meta:
        model = UsesIngredient

    ingredient = AutoCompleteSelectIngredientField()
    group = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput(attrs={'class': 'group'}))
    amount = forms.FloatField(widget=forms.TextInput(attrs={'class': 'amount'}))
    
    def __init__(self, *args, **kwargs):
        form = super(UsesIngredientForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            self.fields['unit'].queryset = self.instance.ingredient.useable_units.all()
        return form

    def _get_changed_data(self, *args, **kwargs):
        super(UsesIngredientForm, self)._get_changed_data(*args, **kwargs)
        # If group is in changed_data, but no other fields are filled in, remove group so
        # the form will not be validated or saved
        if 'group' in self._changed_data and len(self._changed_data) == 1:
            contains_data = False
            for name in ['ingredient', 'amount', 'unit']:
                field = self.fields[name]
                prefixed_name = self.add_prefix(name)
                data_value = field.widget.value_from_datadict(self.data, self.files, prefixed_name)
                if data_value:
                    contains_data = True
                    break
            if not contains_data:
                self._changed_data.remove('group')
        return self._changed_data
    changed_data = property(_get_changed_data)

class IngredientsFormSet(BaseInlineFormSet):
    """
    Require at least one form in the formset to be completed.
    
    """
    unknown_ingredients = []
    unknown_ingredients_allowed = False
    
    def clean(self):
        # TODO: fix so that when a certain parameter is given, unknown ingredient errors are ignored
        super(IngredientsFormSet, self).clean()
        if any(len(errors) > 0 for errors in self.errors):
            # Check if any errors were made except unknown ingredient errors
            for form in self.forms:
                errors = dict(form.errors)
                if len(errors) <= 0:
                    continue
                if not 'ingredient' in errors:
                    # Ingredient doesn't have errors
                    return self
                unknown_ing_error_msg = form['ingredient'].field.unknown_ingredient_error_message
                if len(errors) > 1:
                    # Multiple fields have errors
                    if 'ingredient' in errors:
                        for i in range(len(errors['ingredient'])):
                            if unknown_ing_error_msg in errors['ingredient'][i]:
                                del form.errors['ingredient'][i]
                                break
                    return self
                if len(errors['ingredient']) > 1 or not unknown_ing_error_msg in errors['ingredient'][0]:
                    # Ingredient field has multiple errors, or not the error we are looking for
                    return self
            
            # Only unknown ingredient errors after this point
            unknown_ingredients = []
            for form in self.forms:
                if form.errors:
                    # If the form has errors, we known its an unknown ingredient error
                    unknown_ingredients.append({'name': form['ingredient'].value(),
                                                'unit': form.cleaned_data['unit']})
                    form._errors = ErrorDict()
            self._errors = self.error_class()
            self.unknown_ingredients = unknown_ingredients
            if self.unknown_ingredients_allowed:
                return self
            raise ValidationError('Unknown ingredients found')
        
        # Check that at least one form has been completed.
        completed = 0
        for cleaned_data in self.cleaned_data:
            # form has data and we aren't deleting it.
            if cleaned_data and not cleaned_data.get('DELETE', False):
                completed += 1

        if completed < 1:
            raise forms.ValidationError("At least one %s is required." %
                self.model._meta.object_name.lower())

class EditRecipeIngredientsForm(FormContainer):
    
    ingredients_general_info = EditRecipeIngredientInfoForm
    ingredients = inlineformset_factory(Recipe, UsesIngredient, extra=1,
                                        form=UsesIngredientForm, formset=IngredientsFormSet)
    
    def is_valid(self):
        valid = self.forms['ingredients_general_info'].is_valid()
        if valid and 'request_unknown_ingredients' in self.forms['ingredients_general_info'].cleaned_data and self.forms['ingredients_general_info'].cleaned_data['request_unknown_ingredients']:
            self.forms['ingredients'].unknown_ingredients_allowed = True
        return valid & self.forms['ingredients'].is_valid()


class EditRecipeInstructionsForm(forms.ModelForm):
    
    class Meta:
        model = Recipe
        fields = ['active_time', 'passive_time', 'instructions']
    
    instructions = forms.CharField(widget=MarkItUpWidget(markitup_set='js/recipes'))
    
    def save(self):
        super(EditRecipeInstructionsForm, self).save()
    

class SearchRecipeForm(forms.Form):
    
    SORT_CHOICES = (('name', 'Naam'), ('footprint', 'Voetafdruk'),
                    ('active_time', 'Actieve Kooktijd'), ('tot_time', 'Totale Kooktijd'))
    SORT_ORDER_CHOICES = (('', 'Van Laag naar Hoog'), ('-', 'Van Hoog naar Laag'))
    OPERATOR_CHOICES = (('and', 'Allemaal'), ('or', 'Minstens 1'))
    
    search_string = forms.CharField(required=False, label='Zoektermen',
                                    widget=forms.TextInput(attrs={'placeholder': 'Zoek recepten', 'class': 'keywords-searchbar'}))
    
    advanced_search = forms.BooleanField(initial=True, required=False)
    
    sort_field = forms.ChoiceField(choices=SORT_CHOICES)
    sort_order = forms.ChoiceField(widget=RadioSelect, choices=SORT_ORDER_CHOICES, required=False)
    
    ven = forms.BooleanField(initial=True, required=False, label='Veganistisch')
    veg = forms.BooleanField(initial=True, required=False, label='Vegetarisch')
    nveg = forms.BooleanField(initial=True, required=False, label='Niet-Vegetarisch')
    
    cuisine = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all(), required=False, label='Keuken',
                                             widget=CheckboxSelectMultiple())
    
    course = forms.MultipleChoiceField(required=False, choices=recipes.models.Recipe.COURSES, label='Maaltijd',
                                       widget=CheckboxSelectMultiple())
    
    include_ingredients_operator = forms.ChoiceField(widget=RadioSelect, choices=OPERATOR_CHOICES, label='', initial=OPERATOR_CHOICES[1][0])

class IngredientInRecipeSearchForm(forms.Form):
    
    name = forms.CharField()
    
    

