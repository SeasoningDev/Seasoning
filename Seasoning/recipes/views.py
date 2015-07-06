'''
Created on Jul 5, 2015

@author: joep
'''
from django.shortcuts import render
from recipes.models import Recipe
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http.response import JsonResponse
from django.template.loader import render_to_string

def browse_recipes(request):
    return render(request, 'recipes/browse_recipes.html')



def get_recipes(request, results_per_page=10):
    results_per_page = min(int(results_per_page), 100)
    
    paginator = Paginator(Recipe.objects.prefetch_related('uses_ingredient__ingredient__available_in_country__transport_method',
                                                          'uses_ingredient__ingredient__available_in_country__location',
                                                          'uses_ingredient__ingredient__available_in_sea__transport_method',
                                                          'uses_ingredient__ingredient__available_in_sea__location',
                                                          'uses_ingredient__unit').filter(external_url__isnull=False).order_by('name'), results_per_page)
    
    page = int(request.GET.get('page', 1))
    try:
        recipes_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        recipes_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        recipes_page = paginator.page(paginator.num_pages)
    
    recipe_previews_html = ''
    for recipe in recipes_page:
        recipe_previews_html += render_to_string('recipes/includes/recipe_preview.html', {'recipe': recipe})
        
    more_pages = recipes_page.has_next()
    
    return JsonResponse(data={'result': recipe_previews_html,
                              'more_pages': more_pages}, safe=False)
    
    
    
    