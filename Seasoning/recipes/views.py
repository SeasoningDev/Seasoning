'''
Created on Jul 5, 2015

@author: joep
'''
from django.shortcuts import render, get_object_or_404
from recipes.models import Recipe, RecipeDistribution
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http.response import JsonResponse, Http404
from django.template.loader import render_to_string
from recipes.forms import RecipeSearchForm, IngredientInRecipeSearchForm
from django.forms.formsets import formset_factory
from django.template.context import RequestContext
import datetime
from ingredients.models import AvailableIn
from decimal import Decimal

def browse_recipes(request):
    IngredientInRecipeFormset = formset_factory(IngredientInRecipeSearchForm, extra=0)
    
    recipe_search_form = RecipeSearchForm()
        
    include_ingredients_formset = IngredientInRecipeFormset(prefix='include')
    exclude_ingredients_formset = IngredientInRecipeFormset(prefix='exclude')
    
    return render(request, 'recipes/browse_recipes.html', {'recipe_search_form': recipe_search_form,
                                                           'include_ingredients_formset': include_ingredients_formset,
                                                           'exclude_ingredients_formset': exclude_ingredients_formset})

def view_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.save()
    
    return render(request, 'recipes/view_recipe.html', {'recipe': recipe})

def view_recipe_footprint_analysis(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    return render(request, 'recipes/view_recipe_footprint_analysis.html', {'recipe': recipe})



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
            recipe_queryset = Recipe.objects.all()
            
    else:
        page = 1
        recipe_queryset = Recipe.objects.all()
    
    
    paginator = Paginator(recipe_queryset, results_per_page)
    
    try:
        try:
            recipes_page = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            recipes_page = paginator.page(1)
        
        recipe_previews_html = ''
        for recipe in recipes_page:
            recipe_previews_html += render_to_string('recipes/includes/recipe_preview.html', RequestContext(request, {'recipe': recipe}))
            
        has_next = recipes_page.has_next()
            
    except EmptyPage:
        recipe_previews_html = ''
        has_next = False
    
    
    return JsonResponse(data={'result': recipe_previews_html,
                              'has_next': has_next, 
                              'result_count': paginator.count}, safe=False)
    
    
    
def get_recipe_footprint_breakdown_data(request, recipe_id):
    try:
        recipe = Recipe.objects.prefetch_related('uses_ingredients__ingredient__can_use_units__unit',
                                                 'uses_ingredients__ingredient__available_in_country__location',
                                                 'uses_ingredients__ingredient__available_in_country__transport_method',
                                                 'uses_ingredients__ingredient__available_in_sea__location',
                                                 'uses_ingredients__ingredient__available_in_sea__transport_method',
                                                 'uses_ingredients__unit__parent_unit').get(id=recipe_id)
    except Recipe.DoesNotExist:
        raise Http404
    
    footprint_data = []
    
    for month in range(13):
        date = datetime.date(year=AvailableIn.BASE_YEAR + (month // 12),
                             month=(month % 12) + 1,
                             day=1)
        month_data = {'date': date}
        
        for uses_ingredient in recipe.uses_ingredients.all():
            month_data[uses_ingredient.ingredient.name] = {source: footprint / float(recipe.portions) for source, footprint in uses_ingredient.footprint_breakdown(date).items()}
        
        footprint_data.append(month_data)
        
    return JsonResponse(data={'current_date': datetime.date.today().replace(year=AvailableIn.BASE_YEAR),
                              'footprint_data': footprint_data}, safe=False)

def get_recipe_relative_footprint_data(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    return JsonResponse(data={'this_recipes_footprint': recipe.cached_footprint,
                              'all_recipes_footprints': [r[0] for r in Recipe.objects.all().values_list('cached_footprint')],
                              'all_recipes_distribution': list(RecipeDistribution.objects.filter(group=RecipeDistribution.ALL).values('parameter', 'parameter_value')),
                              'same_course_recipes_footprints': [r[0] for r in Recipe.objects.filter(course=recipe.course).values_list('cached_footprint')],
                              'same_course_recipes_distribution': list(RecipeDistribution.objects.filter(group=recipe.course).values('parameter', 'parameter_value')),
                              'same_veganism_recipes_footprints': [r[0] for r in Recipe.objects.filter(cached_veganism=recipe.cached_veganism).values_list('cached_footprint')],
                              'same_veganism_recipes_distribution': list(RecipeDistribution.objects.filter(group=RecipeDistribution.ALL).values('parameter', 'parameter_value')),
                              'both_same_recipes_footprints': [r[0] for r in Recipe.objects.filter(course=recipe.course, cached_veganism=recipe.cached_veganism).values_list('cached_footprint')],
                              'both_same_recipes_distribution': list(RecipeDistribution.objects.filter(group=RecipeDistribution.ALL).values('parameter', 'parameter_value'))}, safe=False)
