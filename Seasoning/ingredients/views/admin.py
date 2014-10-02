from django.core.exceptions import PermissionDenied
from ingredients.models import Ingredient
from django.shortcuts import render

def list_ingredients(request):
    """
    Displays a list of all ingredients currently in the database.
    
    """    
    if not request.user.is_superuser:
        raise PermissionDenied
   
    ingredients = Ingredient.objects.all().order_by('accepted', 'name')
    ao_ingredients = len(ingredients)
    ao_accepted = len(filter(lambda x: x.accepted==True, ingredients))
    perc_accepted = int(ao_accepted/float(ao_ingredients)*100)
    ao_bramified = len(filter(lambda x: x.bramified==True, ingredients))
    perc_bramified = int(ao_bramified/float(ao_ingredients)*100)
    
    return render(request, 'admin/list_ingredients.html', {'ingredients': ingredients,
                                                           'ao_ingredients': ao_ingredients,
                                                           'perc_accepted': perc_accepted,
                                                           'ao_accepted': ao_accepted,
                                                           'perc_bramified': perc_bramified,
                                                           'ao_bramified': ao_bramified,})