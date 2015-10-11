'''
Created on Jul 7, 2015

@author: joep
'''
from django.views.decorators.csrf import csrf_exempt
from ingredients.models import Ingredient, Synonym
from django.http.response import JsonResponse

@csrf_exempt
def get_ingredient_name_list(request):
    query = request.GET.get('term', '')
    
    # Query the database for ingredients with a name or synonym like the query
    ingredients = list(Ingredient.objects.filter(name__icontains=query, accepted=True).values_list('id', 'name').order_by('name'))
    print(Synonym.objects.filter(name__icontains=query, ingredient__accepted=True))
    ingredients.extend(Synonym.objects.filter(name__icontains=query, ingredient__accepted=True).values_list('ingredient_id', 'name').order_by('name'))
    
    # Convert results to dict
    result = [{'label': name, 'value': ing_id} for (ing_id, name) in sorted(ingredients, key=lambda x: x[1])]
  
    # Return the response
    return JsonResponse(result, safe=False)
    
