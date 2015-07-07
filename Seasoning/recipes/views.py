'''
Created on Jul 5, 2015

@author: joep
'''
from django.shortcuts import render
from recipes.models import Recipe
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http.response import JsonResponse
from django.template.loader import render_to_string
from recipes.forms import RecipeSearchForm, IngredientInRecipeSearchForm
from django.forms.formsets import formset_factory

def browse_recipes(request):
    IngredientInRecipeFormset = formset_factory(IngredientInRecipeSearchForm, extra=0)
    
    recipe_search_form = RecipeSearchForm()
        
    include_ingredients_formset = IngredientInRecipeFormset(prefix='include')
    exclude_ingredients_formset = IngredientInRecipeFormset(prefix='exclude')
    
    return render(request, 'recipes/browse_recipes.html', {'recipe_search_form': recipe_search_form,
                                                           'include_ingredients_formset': include_ingredients_formset,
                                                           'exclude_ingredients_formset': exclude_ingredients_formset})



def get_recipes(request, results_per_page=10):
    results_per_page = min(int(results_per_page), 100)
    
    IngredientInRecipeFormset = formset_factory(IngredientInRecipeSearchForm, extra=0)
    
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        
        recipe_search_form = RecipeSearchForm(request.POST)
        
        include_ingredients_formset = IngredientInRecipeFormset(request.POST, prefix='include')
        exclude_ingredients_formset = IngredientInRecipeFormset(request.POST, prefix='exclude')
            
        
        if recipe_search_form.is_valid() and include_ingredients_formset.is_valid() and exclude_ingredients_formset.is_valid:
            include_ingredient_names = [form.cleaned_data['name'] for form in include_ingredients_formset if 'name' in form.cleaned_data]
            exclude_ingredient_names = [form.cleaned_data['name'] for form in exclude_ingredients_formset if 'name' in form.cleaned_data]
        
            recipe_queryset = recipe_search_form.search_queryset(include_ingredient_names=include_ingredient_names,
                                                                 exclude_ingredient_names=exclude_ingredient_names)
        
        else:
            print(recipe_search_form.errors)
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
    
    
    return JsonResponse(data={'result': recipe_previews_html,
                              'result_count': paginator.count}, safe=False)
    
    
    
    