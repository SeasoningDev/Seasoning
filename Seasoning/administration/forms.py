'''
Created on Jul 7, 2015

@author: joep
'''
from django import forms
from recipes.models import ScrapedRecipe

class ScrapedRecipeProofreadForm(forms.ModelForm):
    
    class Meta:
        model = ScrapedRecipe
        exclude = ['scraped_name', 'external', 'external_site', 'external_url',
                   'description', 'active_time', 'passive_time',
                   'extra_info', 'instructions', 'deleted', 'recipe',
                   'image_url', 'course_proposal', 'cuisine_proposal']