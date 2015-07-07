'''
Created on Jul 6, 2015

@author: joep
'''
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from recipes.scrapers.eva_scraper import scrape_recipes
from recipes.models import ScrapedRecipe, ScrapedUsesIngredient
from administration.forms import ScrapedRecipeProofreadForm
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError
from django.contrib import messages

@staff_member_required
def admin_home(request):
    return render(request, 'admin/admin_base.html')

@staff_member_required
def admin_scrapers(request):
    return render(request, 'admin/admin_scrapers.html', {'scraped_recipes': {'eva': ScrapedRecipe.objects.filter(external_site__name__icontains='eva').count()}})

@staff_member_required
def admin_scrape_eva(request):
    ScrapedRecipe.objects.all().delete()
    
    scrape_recipes()
    
    return redirect('admin_scrapers')

@staff_member_required
def admin_proofread_scraped_recipes(request):
    unfinished_recipes = sorted(sorted(ScrapedRecipe.objects.select_related('cuisine').prefetch_related('ingredients__ingredient',
                                                                                                        'ingredients__unit').filter(recipe=None), key=lambda recipe: recipe.ao_unknown_ingredients()), key=lambda recipe: recipe.is_missing_info())
    finished_recipes = ScrapedRecipe.objects.exclude(recipe=None)
    
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