from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe, UsesIngredient
from django.http.response import Http404, HttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
import json
import datetime
from ingredients.models import Ingredient, Unit
from django.forms.formsets import formset_factory
from recipes.forms import IngredientInRecipeSearchForm, SearchRecipeForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def ajax_recipe_ingredients(request, recipe_id, portions):
    try:
        portions = int(portions)
        if request.is_ajax() and portions >= 1:
            try:
                recipe = Recipe.objects.get(pk=recipe_id)
                usess = UsesIngredient.objects.select_related('ingredient', 'unit').filter(recipe=recipe).order_by('group', 'ingredient__name')
                
                ratio = float(portions)/recipe.portions
                total_footprint = portions * recipe.footprint
                
                for uses in usess:
                    uses.save_allowed = False
                    uses.amount = ratio * uses.amount
                    uses.footprint = ratio * uses.footprint()
                
                data = {'ingredient_list': render_to_string('includes/ingredient_list.html', {'usess': usess,
                                                                                              'total_footprint': total_footprint})}
                json_data = json.dumps(data)
                
                return HttpResponse(json_data)
            
            except Recipe.DoesNotExist, UsesIngredient.DoesNotExist:
                pass
    except TypeError:
        pass
    
    raise PermissionDenied
    
@csrf_exempt
@login_required
def upvote(request, recipe_id):
    if request.is_ajax():
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        recipe.upvote(user=request.user.id)
        return HttpResponse(recipe.upvotes)
        
    raise PermissionDenied
    

@login_required
def downvote(request, recipe_id):
    if request.is_ajax():
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        recipe.downvote(user=request.user.id)
        return HttpResponse(recipe.upvotes)
        
    raise PermissionDenied

@csrf_exempt
def get_recipe_footprint_evolution(request):
    
    if request.is_ajax() and request.method == 'POST':
        recipe_id = request.POST.get('recipe', None)
    
        if recipe_id is not None:
            try:
                recipe = Recipe.objects.prefetch_related('uses__unit',
                                                         'uses__ingredient__canuseunit_set__unit',
                                                         'uses__ingredient__available_in_country__location',
                                                         'uses__ingredient__available_in_country__transport_method',
                                                         'uses__ingredient__available_in_sea__location',
                                                         'uses__ingredient__available_in_sea__transport_method').get(pk=recipe_id)
                footprints = recipe.monthly_footprint()
                footprints.append(footprints[-1])
                footprints.insert(0, footprints[0])
                data = {'footprints': footprints,
                        'doy': datetime.date.today().timetuple().tm_yday}
                json_data = json.dumps(data)
            
                return HttpResponse(json_data)
            except Recipe.DoesNotExist, UsesIngredient.DoesNotExist:
                raise Http404
        
    raise PermissionDenied

@csrf_exempt
def ajax_ingredient_units(request):
    if request.method == 'POST' and request.is_ajax():
        name = request.POST.get('ingredient_name', '')
        try:
            units = Ingredient.objects.accepted_with_name(name).useable_units.all().values('id', 'name')
        except Ingredient.DoesNotExist:
            units = Unit.objects.all().values('id', 'name')
        data = json.dumps({unit['id']: unit['name'] for unit in units})
        return HttpResponse(data)
    raise PermissionDenied()

def ajax_markdown_preview(request):
    if request.method == 'POST' and request.is_ajax():
        markdown = request.POST.get('data', '')
        return render(request, 'recipes/markdown_preview.html', {'markdown_text': markdown})
    raise PermissionDenied()

def ajax_browse_recipes(request):
    if request.method == 'POST' and request.is_ajax():
        # This is a formset for inputting ingredients to be included or excluded in the recipe search
        IngredientInRecipeFormset = formset_factory(IngredientInRecipeSearchForm, extra=1)
    
        page = 1
        search_form = SearchRecipeForm(request.POST)
        
        include_ingredients_formset = IngredientInRecipeFormset(request.POST, prefix='include')
        exclude_ingredients_formset = IngredientInRecipeFormset(request.POST, prefix='exclude')
        
        if search_form.is_valid() and include_ingredients_formset.is_valid() and exclude_ingredients_formset.is_valid():
            data = search_form.cleaned_data
            include_ingredient_names = [form.cleaned_data['name'] for form in include_ingredients_formset if 'name' in form.cleaned_data]
            exclude_ingredient_names = [form.cleaned_data['name'] for form in exclude_ingredients_formset if 'name' in form.cleaned_data]
            recipes_list = Recipe.objects.query(search_string=data['search_string'], advanced_search=data['advanced_search'],
                                                sort_field=data['sort_field'], sort_order=data['sort_order'], inseason=data['inseason'], ven=data['ven'], 
                                                veg=data['veg'], nveg=data['nveg'], cuisines=data['cuisine'], courses=data['course'], 
                                                include_ingredients_operator=data['include_ingredients_operator'],
                                                include_ingredient_names=include_ingredient_names, exclude_ingredient_names=exclude_ingredient_names)
        page = search_form.cleaned_data['page']
        
        # Split the result by 12
        paginator = Paginator(recipes_list, 12, allow_empty_first_page=False)
        
        try:
            recipes = paginator.page(page)
        except PageNotAnInteger:
            recipes = paginator.page(1)
        except EmptyPage:
            raise Http404()
        
        search_form_id = 'recipe-search-form'
    
        return render(request, 'includes/recipe_summaries.html', {'recipes': recipes,
                                                                  'search_form_id': search_form_id})
        
    raise PermissionDenied()
