from ingredients.forms import SearchIngredientForm
from django.shortcuts import render
from ingredients.models import Ingredient
from django.http.response import Http404

def browse_ingredients(request):
    
    search_form = SearchIngredientForm()
        
    search_form_id = 'browse-ingredients-form'
    
    return render(request, 'ingredients/browse_ingredients.html', {'form': search_form,
                                                                   'search_form_id': search_form_id})
    
def view_ingredient(request, ingredient_id):
    try:
        ingredient = Ingredient.objects.prefetch_related(
            'synonyms',
            'available_in_country__location',
            'available_in_country__transport_method',
            'available_in_sea__location',
            'available_in_sea__transport_method',
            'canuseunit_set__unit').get(pk=ingredient_id, accepted=True)
    except Ingredient.DoesNotExist:
        raise Http404
    
    return render(request, 'ingredients/view_ingredient.html', {'ingredient': ingredient})
