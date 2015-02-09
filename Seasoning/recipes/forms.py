from django import forms
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from ingredients.fields import AutoCompleteSelectIngredientField
from recipes.models import Recipe, Cuisine, RecipeImage
from recipes.models.t_recipe import IncompleteRecipe, TemporaryUsesIngredient
from recipes.models.recipe import UsesIngredient
from recipes.fields import MultipleSeparatorsFloatField,\
    ChooseRealDisplayTempUnitField
from django.forms.utils import ErrorDict
    

class EditRecipeForm(forms.ModelForm):
    
    class Meta:
        model = Recipe
        fields = ('name', 'active_time', 'passive_time', 'course', 'cuisine', 
                  'description', 'portions', 'extra_info', 'instructions')
        widgets = {
            'active_time': forms.widgets.TextInput(),
            'passive_time': forms.widgets.TextInput(),
            'portions': forms.widgets.TextInput(),
        }
        

class EditIncompleteRecipeForm(forms.ModelForm):
    
    class Meta:
        model = IncompleteRecipe
        fields = ('name', 'active_time', 'passive_time', 'course', 'cuisine', 
                  'description', 'portions', 'extra_info', 'instructions')
        widgets = {
            'active_time': forms.widgets.TextInput(),
            'passive_time': forms.widgets.TextInput(),
            'portions': forms.widgets.TextInput(),
        }
        


class TemporaryUsesIngredientForm(forms.ModelForm):
    
    class Meta:
        model = TemporaryUsesIngredient
        exclude = ('ingredient', )
    
    amount = MultipleSeparatorsFloatField(widget=forms.TextInput(attrs={'class': 'amount'}))
    unit = ChooseRealDisplayTempUnitField()
    
    
    def __init__(self, *args, **kwargs):
        result = super(TemporaryUsesIngredientForm, self).__init__(*args, **kwargs)
        if self.instance is not None:
            if self.instance.unit.unit is None:
                self.initial['unit'] = None
            else:
                self.initial['unit'] = self.instance.unit.unit.pk
        
        return result
    
    def full_clean(self, *args, **kwargs):
        if self.has_changed():
            return super(TemporaryUsesIngredientForm, self).full_clean(*args, **kwargs)
        self._errors = ErrorDict()
        self.cleaned_data = self.initial
        return
    
    def clean(self, *args, **kwargs):
        cleaned_data = super(TemporaryUsesIngredientForm, self).clean(*args, **kwargs)
        if 'unit' in cleaned_data and self.instance is not None:
            cleaned_data['real_unit'] = cleaned_data['unit']
            cleaned_data['unit'] = self.instance.unit
        return cleaned_data
    
    def save(self, *args, **kwargs):
        if self.instance is not None and 'real_unit' in self.cleaned_data:
            self.instance.unit.unit = self.cleaned_data['real_unit']
            self.instance.unit.save()
        return super(TemporaryUsesIngredientForm, self).save(*args, **kwargs)

class UsesIngredientForm(forms.ModelForm):
    
    class Meta:
        model = UsesIngredient
        exclude = []

    ingredient = AutoCompleteSelectIngredientField()
    group = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput(attrs={'class': 'group'}))
    amount = MultipleSeparatorsFloatField(widget=forms.TextInput(attrs={'class': 'amount'}))
    
    def clean(self, *args, **kwargs):
        cleaned_data = super(UsesIngredientForm, self).clean(*args, **kwargs)
        
        if cleaned_data['ingredient'].is_dummy():
            cleaned_data[UsesIngredient.UNKNOWN_INGREDIENT_FIELD] = self.data['{}-ingredient-text'.format(self.prefix)]
            
        return cleaned_data
    
    def save(self, *args, **kwargs):
        if UsesIngredient.UNKNOWN_INGREDIENT_FIELD in self.cleaned_data:
            setattr(self.instance, UsesIngredient.UNKNOWN_INGREDIENT_FIELD, self.cleaned_data[UsesIngredient.UNKNOWN_INGREDIENT_FIELD])
        return super(UsesIngredientForm, self).save(*args, **kwargs)
    
    
#     def _get_changed_data(self, *args, **kwargs):
#         super(UsesIngredientForm, self)._get_changed_data(*args, **kwargs)
#         # If group is in changed_data, but no other fields are filled in, remove group so
#         # the form will not be validated or saved
#         if 'group' in self._changed_data and len(self._changed_data) == 1:
#             contains_data = False
#             for name in ['ingredient', 'amount', 'unit']:
#                 field = self.fields[name]
#                 prefixed_name = self.add_prefix(name)
#                 data_value = field.widget.value_from_datadict(self.data, self.files, prefixed_name)
#                 if data_value:
#                     contains_data = True
#                     break
#             if not contains_data:
#                 self._changed_data.remove('group')
#         return self._changed_data
#     changed_data = property(_get_changed_data)
    

class SearchRecipeForm(forms.Form):
    
    SORT_CHOICES = (('time_added', 'Datum toegevoegd (Jongste eerst)'), ('-time_added', 'Datum toegevoegd (Oudste eerst)'),
                    ('footprint', 'Voetafdruk (Laagste eerst)'), ('-footprint', 'Voetafdruk (Hoogste eerst)'),                    
                    ('name', 'Naam (Alfabetisch)'), ('-name', 'Naam (Omgekeerd alfabetisch)'), 
                    ('rating', 'Waardering (Hoogste eerst)'), ('-rating', 'Waardering (Laagste eerst)'), 
                    ('active_time', 'Actieve kooktijd (Kortste eerst)'), ('-active_time', 'Actieve kooktijd (Langste eerst)'), 
                    ('tot_time', 'Totale kooktijd (Kortste eerst)'), ('-tot_time', 'Totale kooktijd (Langste eerst)'))
    OPERATOR_CHOICES = (('and', 'Allemaal'), ('or', 'Minstens 1'))
    
    search_string = forms.CharField(required=False, label='Zoektermen',
                                    widget=forms.TextInput(attrs={'placeholder': 'Zoek recepten', 'class': 'keywords-searchbar'}))
    
    advanced_search = forms.BooleanField(initial=False, required=False)
    
    sort_field = forms.ChoiceField(choices=SORT_CHOICES, initial=SORT_CHOICES[0][0])
    
    inseason = forms.BooleanField(initial=False, required=False)
    
    ven = forms.BooleanField(initial=True, required=False, label='Veganistisch')
    veg = forms.BooleanField(initial=True, required=False, label='Vegetarisch')
    nveg = forms.BooleanField(initial=True, required=False, label='Niet-Vegetarisch')
    
    cuisine = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all(), required=False, label='Keuken',
                                             widget=CheckboxSelectMultiple())
    
    course = forms.MultipleChoiceField(required=False, choices=Recipe.COURSES, label='Maaltijd',
                                       widget=CheckboxSelectMultiple())
    
    include_ingredients_operator = forms.ChoiceField(widget=RadioSelect, choices=OPERATOR_CHOICES, label='', initial=OPERATOR_CHOICES[1][0], required=False)
    
    page = forms.IntegerField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}), initial=0)

class IngredientInRecipeSearchForm(forms.Form):
    
    name = forms.CharField()

class UploadRecipeImageForm(forms.ModelForm):
    
    class Meta:
        model = RecipeImage
        fields = ('image', )
    