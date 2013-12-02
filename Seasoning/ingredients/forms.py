from django import forms

class SearchIngredientForm(forms.Form):
    
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Zoek ingredienten', 'class': 'keywords-searchbar'}),
                           required=False)