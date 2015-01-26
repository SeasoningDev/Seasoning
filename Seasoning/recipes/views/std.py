from django.forms.formsets import formset_factory
from recipes.forms import IngredientInRecipeSearchForm, SearchRecipeForm,\
    UploadRecipeImageForm, EditRecipeForm, AddRecipeForm, UsesIngredientForm
from django.shortcuts import render, get_object_or_404, redirect
from recipes.models import Recipe, RecipeImage
from django.http.response import Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from recipes.models.recipe import Upvote, UsesIngredient
from recipes.models.t_recipe import IncompleteRecipe, TemporaryIngredient,\
    TemporaryUsesIngredient
from django.forms.models import inlineformset_factory
from ingredients.models.ingredients import Ingredient


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
        recipe = Recipe.objects.select_related('author', 'cuisine').get(pk=recipe_id)
    except Recipe.DoesNotExist:
        raise Http404
    
    user_has_upvoted = Upvote.objects.filter(recipe_id=recipe_id, user=request.user.id).exists()
    
    total_time = recipe.active_time + recipe.passive_time
    if total_time > 0:
        active_time_perc = str((float(recipe.active_time) / total_time) * 100).replace(',', '.')
        passive_time_perc = str(100 - (float(recipe.active_time) / total_time) * 100).replace(',', '.')
        
        context['active_time_perc'] = active_time_perc
        context['passive_time_perc'] = passive_time_perc
    
    template = 'recipes/view_recipe.html'
    
    context['recipe'] = recipe
    context['user_has_upvoted'] = user_has_upvoted
    context['total_time'] = total_time
    
    upload_image_form = UploadRecipeImageForm()
    context['upload_image_form'] = upload_image_form
    
    return render(request, template, context)

@login_required
def view_incomplete_recipe(request, recipe_id):
    recipe = get_object_or_404(IncompleteRecipe, id=recipe_id, author=request.user)
    
    if request.method == 'POST':
        upload_image_form = UploadRecipeImageForm(request.POST, request.FILES)
        if upload_image_form.is_valid():
            image = upload_image_form.save(commit=False)
            image.recipe = recipe
            image.added_by = request.user
            image.save()
            
            upload_image_form = UploadRecipeImageForm()
    else:
        upload_image_form = UploadRecipeImageForm()
    
    return render(request, 'recipe/view_recipe.html', {'recipe': recipe,
                                                       'upload_image_form': upload_image_form})

@login_required
def delete_recipe_image(request, image_id):
    image = get_object_or_404(RecipeImage, pk=image_id)
    
    if image.added_by == request.user or image.recipe.author == request.user or request.user.is_staff:
        recipe = image.recipe
        image.delete()
        messages.add_message(request, messages.SUCCESS, 'De afbeelding werd met succes verwijderd.')
        return redirect(reverse('view_recipe', args=(recipe.id, )))
        
    raise PermissionDenied()

@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    
    if recipe.author == request.user:
        recipe.delete()
        messages.add_message(request, messages.INFO, 'Je recept \'' + recipe.name + '\' werd met succes verwijderd.')
        return redirect('home')
        
        
    raise PermissionDenied()

def external_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    return render(request, 'recipes/external_site_wrapper.html', {'recipe': recipe})


@login_required
def add_recipe(request):
    new_recipe = IncompleteRecipe(author=request.user)
    new_recipe.save()
    
    return redirect(reverse('edit_incomplete_recipe', args=(new_recipe.id, )))

@login_required
def edit_recipe(request, recipe_id, incomplete=False):
    if incomplete:
        recipe = get_object_or_404(IncompleteRecipe, id=recipe_id)
        form = AddRecipeForm(instance=recipe)
        UsesIngredientFormset = inlineformset_factory(IncompleteRecipe, TemporaryUsesIngredient, extra=0)
        ing_formset = UsesIngredientFormset(instance=recipe)
    else:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        form = EditRecipeForm(instance=recipe)
        UsesIngredientFormset = inlineformset_factory(Recipe, UsesIngredient, form=UsesIngredientForm, extra=0)
        ing_formset = UsesIngredientFormset(instance=recipe)
        
    if recipe.author == request.user or request.user.is_staff:
        return render(request, 'recipes/view_recipe.html', {'recipe': recipe,
                                                            'form': form,
                                                            'ing_formset': ing_formset,
                                                            'edit': True})
    
    raise PermissionDenied()

@login_required
def save_recipe(request, recipe_id):
    recipe = get_object_or_404(IncompleteRecipe, id=recipe_id)
    
    if recipe.author == request.user or request.user.is_staff:
        return redirect(reverse('view_recipe', args=(recipe.id, )))
    
    raise PermissionDenied()
