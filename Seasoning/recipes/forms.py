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
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, initial=SORT_CHOICES[0][0], required=False)
    
    def search_queryset(self):
        if not self.is_valid():
            return None
        
        qs = Recipe.objects.filter(name__icontains=self.cleaned_data['search_query'])
        
        if 'sort_by' in self.cleaned_data and self.cleaned_data['sort_by']:
            qs = qs.order_by(self.cleaned_data['sort_by'])
            
        return qs.filter(external_url__isnull=False)