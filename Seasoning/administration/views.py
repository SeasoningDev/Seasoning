'''
Created on Jul 6, 2015

@author: joep
'''
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from recipes.models import ScrapedRecipe, ScrapedUsesIngredient, Recipe
from administration.forms import ScrapedRecipeProofreadForm
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError
from django.contrib import messages
from recipes.forms import RecipeSearchForm
from django.core.management import call_command
from recipes.scrapers.scrapings_saver import INSTALLED_SCRAPERS, scrape_recipes
from recipes.scrapers.kriskookt_scraper import debug_get_recipe_page
from django.http.response import JsonResponse
from _collections import defaultdict

@staff_member_required
def admin_home(request):
    return render(request, 'admin/admin_dashboard.html', {'stats': {'ao_visible_recipes': RecipeSearchForm({}).search_queryset().count(),
                                                                    'last_cache_update': Recipe.objects.all().order_by('last_update_time')[0].last_update_time}})
    
@staff_member_required
def get_admin_recipes_added_data(request):
    dates = []
    total = 0
    for recipe in Recipe.objects.all().values('time_added').order_by('time_added'):
        total += 1
        dates.append({
            'date': recipe['time_added'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            'amount': total
        })
        
    return JsonResponse(dates, safe=False)



@staff_member_required
def admin_list_ingredients(request):
    return render(request, 'admin/admin_list_ingredients.html')


    
@staff_member_required
def admin_recipes_update_cached_properties(request):
    call_command('update_cached_attributes')
    
    call_command('calculate_recipe_distributions')
    
    return redirect('admin_home')



@staff_member_required
def admin_scrapers(request):
    return render(request, 'admin/admin_scrapers.html', {'scraped_recipes': {'eva': ScrapedRecipe.objects.filter(external_site__name__icontains='eva vzw').count(),
                                                                             'kriskookt': ScrapedRecipe.objects.filter(external_site__name__icontains='kris').count(),
                                                                             'evassmulhuisje': ScrapedRecipe.objects.filter(external_site__name__icontains='smulhuisje').count()}})

@staff_member_required
def admin_scrape_recipes(request, scraper):
    scraper = int(scraper)
    if scraper not in INSTALLED_SCRAPERS:
        messages.add_message(request, messages.ERROR, 'This scraper has not been installed yet')
        
    else:
        scrape_recipes(scraper)
    
    return redirect('admin_scrapers')

@staff_member_required
def admin_proofread_scraped_recipes(request):
    unfinished_recipes = sorted(sorted(sorted(ScrapedRecipe.objects.select_related('cuisine', 'external_site').prefetch_related('ingredients__ingredient',
                                                                                                                                'ingredients__unit').filter(recipe=None), 
                                              key=lambda recipe: recipe.ao_unknown_ingredients()),
                                       key=lambda recipe: recipe.ao_unfinished_ingredients()), 
                                key=lambda recipe: recipe.is_missing_info())
    finished_recipes = ScrapedRecipe.objects.select_related('recipe').exclude(recipe=None).order_by('recipe__time_added')
    
    return render(request, 'admin/admin_proofread_scraped_recipes.html', {'unfinished_recipes': unfinished_recipes,
                                                                          'unfinished_recipes_count': ScrapedRecipe.objects.filter(recipe=None).count(),
                                                                          'finished_recipes': finished_recipes})

@staff_member_required
def admin_proofread_scraped_recipe(request, scraped_recipe_id):
    recipe = ScrapedRecipe.objects.select_related('cuisine').prefetch_related('ingredients__ingredient',
                                                                              'ingredients__unit').get(id=scraped_recipe_id)
    
    ScrapedUsesIngredientFormSet = inlineformset_factory(ScrapedRecipe, ScrapedUsesIngredient, exclude=['ingredient_proposal', 'unit_proposal', 'amount_proposal', 'group'], extra=0)
    
    if request.method == 'POST':
        proofread_form = ScrapedRecipeProofreadForm(request.POST, instance=recipe)
    
        uses_ingredients_formset = ScrapedUsesIngredientFormSet(request.POST, instance=recipe)
        
        if proofread_form.is_valid() and uses_ingredients_formset.is_valid():
            proofread_form.save()
            uses_ingredients_formset.save()
            
            return redirect('admin_proofread_scraped_recipes')
        
    else:
        proofread_form = ScrapedRecipeProofreadForm(instance=recipe)
    
        uses_ingredients_formset = ScrapedUsesIngredientFormSet(instance=recipe)
    
    return render(request, 'admin/admin_proofread_scraped_recipe.html', {'recipe': recipe,
                                                                         'recipe_form': proofread_form,
                                                                         'uses_ingredients_formset': uses_ingredients_formset})

@staff_member_required
def admin_convert_scraped_recipe(request, scraped_recipe_id):
    recipe = ScrapedRecipe.objects.select_related('cuisine').prefetch_related('ingredients__ingredient',
                                                                              'ingredients__unit').get(id=scraped_recipe_id)
    
    try:                                                                          
        recipe.convert_to_real_recipe()
    except ValidationError as e:
        messages.add_message(request, messages.ERROR, e.message)
                                
    return redirect('admin_proofread_scraped_recipes')