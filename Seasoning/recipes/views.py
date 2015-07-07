'''
Created on Jul 5, 2015

@author: joep
'''
from django.shortcuts import render
from recipes.models import Recipe
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from recipes.forms import RecipeSearchForm

def browse_recipes(request):
    recipe_search_form = RecipeSearchForm()
    
    return render(request, 'recipes/browse_recipes.html', {'recipe_search_form': recipe_search_form})



def get_recipes(request, results_per_page=10):
    results_per_page = min(int(results_per_page), 100)
    
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        recipe_search_form = RecipeSearchForm(request.POST)
        
        if recipe_search_form.is_valid():
            recipe_queryset = recipe_search_form.search_queryset()
        
        else:
            recipe_queryset = Recipe.objects.all()
            
    else:
        page = 1
        recipe_queryset = Recipe.objects.all()
    
    
    paginator = Paginator(recipe_queryset.prefetch_related('uses_ingredients__ingredient__can_use_units__unit',
                                                          'uses_ingredients__ingredient__available_in_country__transport_method',
                                                          'uses_ingredients__ingredient__available_in_country__location',
                                                          'uses_ingredients__ingredient__available_in_sea__transport_method',
                                                          'uses_ingredients__ingredient__available_in_sea__location',
                                                          'uses_ingredients__unit__parent_unit'), results_per_page)
    
    try:
        try:
            recipes_page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            recipes_page = paginator.page(1)
        
        recipe_previews_html = ''
        for recipe in recipes_page:
            recipe_previews_html += render_to_string('recipes/includes/recipe_preview.html', {'recipe': recipe})
            
    except EmptyPage:
        recipe_previews_html = ''
    
    
    return JsonResponse(data={'result': recipe_previews_html}, safe=False)
    
    
    
    