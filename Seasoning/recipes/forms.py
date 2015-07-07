'''
Created on Jul 7, 2015

@author: joep
'''
from django import forms
from recipes.models import Recipe

class RecipeSearchForm(forms.Form):
    
    search_query = forms.CharField(required=False)
    
    SORT_CHOICES = (('_footprint', 'Voetafdruk'),
                    ('name', 'Naam (A->Z)'), ('-name', 'Naam (Z->A)'))
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, initial=SORT_CHOICES[0][0])
    
    def search_queryset(self):
        if not self.is_valid():
            return None
        
        return Recipe.objects.filter(name__icontains=self.cleaned_data['search_query']).order_by(self.cleaned_data['sort_by'])