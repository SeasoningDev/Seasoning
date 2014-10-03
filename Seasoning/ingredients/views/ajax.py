from ingredients.models import Ingredient, Synonym
import json
from django.http.response import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from ingredients.forms import SearchIngredientForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def ajax_ingredient_name_list(request):
    # TODO: rewrite javascript using this view
    """
    An ajax call that returns a json list with every ingredient 
    name or synonym containing the given search query
    
    """    
    if request.method == 'POST' and request.is_ajax():
        query = request.POST.get('query', '')
        
        # Query the database for ingredients with a name of synonym like the query
        names = list(Ingredient.objects.filter(name__icontains=query, accepted=True).values_list('name', flat=True).order_by('name'))
        names.extend(Synonym.objects.filter(name__icontains=query, ingredient__accepted=True).values_list('name', flat=True).order_by('name'))
        
        # Convert results to dict
        result = [dict(zip(['value', 'label'], [name, name])) for name in sorted(names)]
        
        # Serialize to json
        ingredients_json = json.dumps(result)
  
        # Return the response
        return HttpResponse(ingredients_json, content_type='application/javascript')
    
    # If this is not an ajax request, permission is denied
    raise PermissionDenied

def ajax_ingredient_list(request):
    """
    an ajax call that returns an html element containing summaries of all
    ingredients that were found using the parameters in the posts form.
    
    """
    if request.method == 'POST' and request.is_ajax():
        search_form = SearchIngredientForm(request.POST)
        
        if search_form.is_valid():
            ingredient_list = Ingredient.objects.accepted_with_name_like(search_form.cleaned_data['name']).order_by('name')       
            
            # Split the result by 12
            paginator = Paginator(ingredient_list, 12, allow_empty_first_page=False)
            
            page = search_form.cleaned_data['page']
            try:
                ingredients = paginator.page(page)
            except PageNotAnInteger:
                ingredients = paginator.page(1)
            except EmptyPage:
                raise Http404()
                
        else:
            ingredients = []
        
        return render(request, 'includes/ingredient_summaries.html', {'ingredients': ingredients})
    raise PermissionDenied()
        

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