'''
Created on Jul 7, 2015

@author: joep
'''
from django import forms
from recipes.models import Recipe, Cuisine
from ingredients.models import Ingredient
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import Q

class RecipeSearchForm(forms.Form):
    
    search_query = forms.CharField(required=False)
    
    SORT_CHOICES = (('cached_footprint', 'Voetafdruk (oplopend)'), ('-cached_footprint', 'Voetafdruk (aflopend)'),
                    ('name', 'Naam (A->Z)'), ('-name', 'Naam (Z->A)'))
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, initial=SORT_CHOICES[0][0], required=False)
    
    """
    Advanced Search Options
    
    """
    in_season = forms.BooleanField(initial=False, required=False)
    no_endangered = forms.BooleanField(initial=False, required=False)
    
    veganism = forms.MultipleChoiceField(choices=Ingredient.VEGANISMS, widget=CheckboxSelectMultiple,
                                         initial=[Ingredient.VEGAN], required=False)
    
    cuisine = forms.ModelMultipleChoiceField(queryset=Cuisine.objects.all(), required=False, label='Keuken',
                                             widget=CheckboxSelectMultiple())
    
    course = forms.MultipleChoiceField(required=False, choices=Recipe.COURSES, label='Maaltijd',
                                       widget=CheckboxSelectMultiple())
    
    include_ingredients_AND_operator = forms.BooleanField(initial=False, required=False)
    
    def search_queryset(self, include_ingredient_names=[], exclude_ingredient_names=[]):
        if not self.is_valid():
            return None
        
        qs = Recipe.objects
        
        recipe_filter = Q(name__icontains=self.cleaned_data['search_query'])

        if 'in_season' in self.cleaned_data and self.cleaned_data['in_season']:
            recipe_filter &= Q(cached_in_season=True)
        
        if 'no_endangered' in self.cleaned_data and self.cleaned_data['no_endangered']:
            recipe_filter &= Q(cached_has_endangered_ingredients=False)
        
        if 'veganism' in self.cleaned_data and len(self.cleaned_data['veganism']) > 0:
            recipe_filter &= Q(cached_veganism__in=self.cleaned_data['veganism'])
        
        if 'cuisine' in self.cleaned_data and len(self.cleaned_data['cuisine']) > 0:
            recipe_filter &= Q(cuisine__in=self.cleaned_data['cuisine'])
        
        if 'course' in self.cleaned_data and len(self.cleaned_data['course']) > 0:
            recipe_filter &= Q(course__in=self.cleaned_data['course'])
        #TODO: synonyms
        if include_ingredient_names:
            
            if self.cleaned_data['include_ingredients_AND_operator']:
                for ingredient in include_ingredient_names:
                    qs = qs.filter(ingredients__name=ingredient)
            
            else:
                ingredients_filter = Q()
                
                for ingredient in include_ingredient_names:
                    ingredients_filter |= Q(ingredients__name=ingredient)
                
                recipe_filter &= ingredients_filter
        
        qs = qs.filter(recipe_filter)
        
        if exclude_ingredient_names:
            for ingredient in exclude_ingredient_names:
                qs = qs.exclude(ingredients__name=ingredient)
        
        
        if 'sort_by' in self.cleaned_data and self.cleaned_data['sort_by']:
            qs = qs.order_by(self.cleaned_data['sort_by'])
            
        return qs.distinct()
    
    

class IngredientInRecipeSearchForm(forms.Form):
    
    name = forms.CharField()