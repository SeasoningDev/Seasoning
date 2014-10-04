from django.forms.formsets import formset_factory
from recipes.forms import IngredientInRecipeSearchForm, SearchRecipeForm
from django.shortcuts import render, get_object_or_404, redirect
from recipes.models import Recipe, Vote
from django.http.response import Http404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib import comments, messages
from django.contrib.comments.views.moderation import perform_delete

def browse_recipes(request):
    """
    Browse or search through recipes
    
    """
    # This is a formset for inputting ingredients to be included or excluded in the recipe search
    IngredientInRecipeFormset = formset_factory(IngredientInRecipeSearchForm, extra=1)
    
    if request.method == 'POST':
        # A simple search with only the recipe name was done (from the homepage)
        search_form = SearchRecipeForm(request.POST)
    else:
        search_form = SearchRecipeForm()
        
    include_ingredients_formset = IngredientInRecipeFormset(prefix='include')
    exclude_ingredients_formset = IngredientInRecipeFormset(prefix='exclude')
        
    search_form_id = 'recipe-search-form'
        
    return render(request, 'recipes/browse_recipes.html', {'search_form': search_form,
                                                           'include_ingredients_formset': include_ingredients_formset,
                                                           'exclude_ingredients_formset': exclude_ingredients_formset,
                                                           'search_form_id': search_form_id})

def view_recipe(request, recipe_id):
    context = {}
    
    try:
        recipe = Recipe.objects.select_related(
            'author', 'cuisine').prefetch_related(
            'uses__unit',
            'uses__ingredient__canuseunit_set__unit',
            'uses__ingredient__available_in_country__location',
            'uses__ingredient__available_in_country__transport_method',
            'uses__ingredient__available_in_sea__location',
            'uses__ingredient__available_in_sea__transport_method').get(pk=recipe_id)
    except Recipe.DoesNotExist:
        raise Http404
    
    user_vote = None
    if request.user.is_authenticated():
        try:
            user_vote = Vote.objects.get(recipe_id=recipe_id, user=request.user)
        except ObjectDoesNotExist:
            pass
    
    total_time = recipe.active_time + recipe.passive_time
    if total_time > 0:
        active_time_perc = str((float(recipe.active_time) / total_time) * 100).replace(',', '.')
        passive_time_perc = str(100 - (float(recipe.active_time) / total_time) * 100).replace(',', '.')
        
        context['active_time_perc'] = active_time_perc
        context['passive_time_perc'] = passive_time_perc
    
    comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Recipe), object_pk=recipe.id, is_removed=False, is_public=True).select_related('user')
    
    template = 'recipes/view_recipe.html'
    
    context['recipe'] = recipe
    context['user_vote'] = user_vote
    context['total_time'] = total_time 
    context['comments'] = comments
    
    return render(request, template, context)

@login_required
def delete_recipe_comment(request, recipe_id, comment_id):
    comment = get_object_or_404(comments.get_model(), pk=comment_id)
    if comment.user == request.user:
        perform_delete(request, comment)
        messages.add_message(request, messages.INFO, 'Je reactie werd succesvol verwijderd.')
        return redirect(view_recipe, recipe_id)
    else:
        raise PermissionDenied
                    

@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    
    if recipe.author == request.user:
        recipe.delete()
        messages.add_message(request, messages.INFO, 'Je recept \'' + recipe.name + '\' werd met succes verwijderd.')
        return redirect('home')
        
        
    raise PermissionDenied

def external_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    return render(request, 'recipes/external_site_wrapper.html', {'recipe': recipe})

def scrape_recipes(request):
    from recipes.scraper.evascraper import scrape_recipes
    scrape_recipes()
    
    return redirect('browse_recipes')