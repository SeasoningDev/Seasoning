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
from django.shortcuts import render
from ingredients.models import Ingredient, CanUseUnit, Synonym
from django.core.exceptions import PermissionDenied
from django.db import connection, models
import json
from django.http.response import HttpResponse, Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from ingredients.forms import SearchIngredientForm
from django.views.decorators.csrf import csrf_exempt

def view_ingredients(request):
    
    if request.method == 'POST':
        search_form = SearchIngredientForm(request.POST)
        
        if search_form.is_valid():
            ingredient_list = Ingredient.objects.accepted_with_name_like(search_form.cleaned_data['name']).order_by('name')       
        else:
            ingredient_list = []
    else:
        search_form = SearchIngredientForm()
    
        ingredient_list = Ingredient.objects.distinct().filter(accepted=True).order_by('name')
        
    # Split the result by 12
    paginator = Paginator(ingredient_list, 12)
    
    page = request.GET.get('page')
    try:
        ingredients = paginator.page(page)
    except PageNotAnInteger:
        ingredients = paginator.page(1)
    except EmptyPage:
        ingredients = paginator.page(paginator.num_pages)
    
    if request.method == 'POST' and request.is_ajax():
        return render(request, 'includes/ingredient_summaries.html', {'ingredients': ingredients})
    
    # TODO: ajax aanpassen voor ingredients
    
    return render(request, 'ingredients/view_ingredients.html', {'form': search_form,
                                                                 'ingredients': ingredients})
    
def view_ingredient(request, ingredient_id):
    try:
        ingredient = Ingredient.objects.get(pk=ingredient_id)
    except Ingredient.DoesNotExist:
        raise Http404    
    return render(request, 'ingredients/view_ingredient.html', {'ingredient': ingredient})



"""
Ajax calls
"""

def ajax_ingredient_name_list(request):
    """
    An ajax call that returns a json list with every ingredient 
    name or synonym containing the given search query
    
    """    
    if request.is_ajax() and 'term' in request.GET:
        query = request.GET['term']
        
        # Query the database for ingredients with a name of synonym like the query
        names = list(Ingredient.objects.filter(name__icontains=query, accepted=True).values_list('name', flat=True).order_by('name'))
        names.extend(Synonym.objects.filter(name__icontains=query, ingredient__accepted=True).values_list('name', flat=True).order_by('name'))
        
        # Convert results to dict
        result = [dict(zip(['value', 'label'], [name, name])) for name in sorted(names)]
        
        # Serialize to json
        ingredients_json = json.dumps(result)
  
        # Return the response
        return HttpResponse(ingredients_json, mimetype='application/javascript')
    
    # If this is not an ajax request, permission is denied
    raise PermissionDenied

@csrf_exempt
def ajax_ingredient_availability(request):
    """
    An ajax call that returns html containing the availability
    data of the requested ingredient
    
    """
    if request.is_ajax() and request.method == 'POST':
        ingredient_id = request.POST.get('ingredient', '')
        ingredient = Ingredient.objects.get(id=ingredient_id)
        
        return render(request, 'includes/ingredient_moreinfo.html', {'ingredient': ingredient})
    
    raise PermissionDenied


"""
Administrative Functions only below this comment
"""
    
def list_ingredients(request):
    """
    Displays a list of all ingredients currently in the database.
    
    """    
    if not request.user.is_superuser:
        raise PermissionDenied
   
    ingredients = Ingredient.objects.all().order_by('accepted', 'name').prefetch_related('canuseunit_set__unit', 'useable_units', 'available_in_country', 'available_in_sea')
    perc_done = int(len(ingredients)/7)
    
    return render(request, 'admin/list_ingredients.html', {'ingredients': ingredients,
                                                           'perc_done': perc_done})