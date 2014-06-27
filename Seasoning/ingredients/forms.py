from django import forms

class SearchIngredientForm(forms.Form):
    
    name = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off', 'placeholder': 'Zoek ingredienten', 'class': 'keywords-searchbar'}),
                           required=False)
    
    page = forms.IntegerField(widget=forms.HiddenInput(attrs={'autocomplete': 'off'}), initial=0)