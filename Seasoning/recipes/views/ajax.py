from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe, UsesIngredient
from django.http.response import Http404, HttpResponse, HttpResponseServerError
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
import json
import datetime
from django.forms.formsets import formset_factory
from recipes.forms import IngredientInRecipeSearchForm, SearchRecipeForm,\
    EditRecipeForm, UploadRecipeImageForm, AddRecipeForm, UsesIngredientForm,\
    EditTemporaryUsesIngredientForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from recipes.models.t_recipe import IncompleteRecipe, TemporaryUsesIngredient
from django.template import defaultfilters
from general.templatetags.markdown_filter import markdown
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from recipes.models.recipe import RecipeImage
from django.forms.models import inlineformset_factory

def ajax_recipe_ingredients(request, recipe_id, portions, incomplete=False):
    try:
        portions = int(portions)
        if request.is_ajax() and portions >= 1:
            try:
                if incomplete:
                    try:
                        recipe = IncompleteRecipe.objects.get(pk=recipe_id)
                    except IncompleteRecipe.DoesNotExist:
                        raise Http404
                    
                    data = {'ingredient_list': render_to_string('includes/ingredient_list.html', {'usess': recipe.uses.all(),
                                                                                                  'incomplete': True})} 
                else:
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
                    
                    ratio = float(portions)/recipe.portions
                    total_footprint = portions * recipe.footprint
                
                    usess = []
                    for uses in recipe.uses.all():
                        uses.save_allowed = False
                        uses.amount = ratio * uses.amount
                        usess.append(uses)
                
                    data = {'ingredient_list': render_to_string('includes/ingredient_list.html', {'usess': usess,
                                                                                                  'total_footprint': total_footprint})}
                json_data = json.dumps(data)
                
                return HttpResponse(json_data)
            
            except UsesIngredient.DoesNotExist:
                raise Http404
    except TypeError:
        pass
    
    raise PermissionDenied
    
@login_required
def upvote(request, recipe_id):
    if request.is_ajax():
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        recipe.upvote(user=request.user)
        return HttpResponse(recipe.upvotes)
        
    raise PermissionDenied()
    

@login_required
def downvote(request, recipe_id):
    if request.is_ajax():
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        recipe.downvote(user=request.user)
        return HttpResponse(recipe.upvotes)
        
    raise PermissionDenied()

def get_recipe_footprint_evolution(request, recipe_id):
    if request.is_ajax() and request.method == 'GET':
        if recipe_id is not None:
            try:
                recipe = Recipe.objects.prefetch_related('uses__unit',
                                                         'uses__ingredient__canuseunit_set__unit',
                                                         'uses__ingredient__available_in_country__location',
                                                         'uses__ingredient__available_in_country__transport_method',
                                                         'uses__ingredient__available_in_sea__location',
                                                         'uses__ingredient__available_in_sea__transport_method').get(pk=recipe_id)
                footprints = recipe.monthly_footprint(with_dates=True)
                data = [['Maand', 'Voetafdruk', {'role': 'tooltip', 'p': {'html': True}}]]
                for point in footprints:
                    data.append((point[0].strftime('%b'), point[1], '<div style="padding:5px;"><b>{}</b><p style="white-space:nowrap;">{:.2f} kgCO2 per portie</p></div>'.format(point[0].strftime('%B'), point[1])))
                
                data = {'data': data,
                        'doy': datetime.date.today().timetuple().tm_yday}
                json_data = json.dumps(data)
            
                return HttpResponse(json_data)
            except Recipe.DoesNotExist, UsesIngredient.DoesNotExist:
                raise Http404
        
    raise PermissionDenied

# def get_recipe_footprint_distribution(request, parameter, subset, recipe_id):
#     if request.is_ajax() and request.method == 'GET':
#         try:
#             recipe = Recipe.objects.get(pk=recipe_id)
#             
#             data = [['Footprint', 'Probability']]
#             data.extend(recipe.distribution_data())
#             
#             data = {'data': data}
#             
#             return HttpResponse(json.dumps(data))
#         
#         except Recipe.DoesNotExist, UsesIngredient.DoesNotExist:
#             raise Http404
#         
#     raise PermissionDenied()

def ajax_markdown_preview(request):
    if request.method == 'POST' and request.is_ajax():
        markdown = request.POST.get('data', '')
        return render(request, 'recipes/markdown_preview.html', {'markdown_text': markdown})
    raise PermissionDenied()

def ajax_edit_recipe(request, recipe_id, incomplete=False):
    if request.is_ajax() and request.method == 'POST':
        if incomplete:
            try:
                recipe = IncompleteRecipe.objects.prefetch_related(
                    'uses__unit__unit').get(id=recipe_id)
            except IncompleteRecipe.DoesNotExist:
                raise Http404
            
            form = AddRecipeForm(request.POST, instance=recipe)
            UsesIngredientFormset = inlineformset_factory(IncompleteRecipe, TemporaryUsesIngredient, form=EditTemporaryUsesIngredientForm, extra=0)
            ing_formset = UsesIngredientFormset(request.POST, instance=recipe, queryset=recipe.uses.select_related('ingredient__ingredient', 
                                                                                                                   'unit__unit').all())
        else:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            form = EditRecipeForm(request.POST, instance=recipe)
            UsesIngredientFormset = inlineformset_factory(Recipe, UsesIngredient, form=UsesIngredientForm, extra=0)
            ing_formset = UsesIngredientFormset(request.POST, instance=recipe, queryset=recipe.uses.select_related('unit').all())
        
        if form.is_valid() and ing_formset.is_valid():
            form.save()
            ing_formset.save()
            
            if not settings.DEBUG:
                # Notify Bram of non-admins changing a recipe
                if not request.user.is_staff:
                    subject = 'Oh nee! Iemand heeft een recept aangepast :O'
                    message = 'Recept \"{}\" (<a href="https://www.seasoning.be{}">link</a>) aangepast door {}'.format(recipe.name,
                                                                                                          reverse('view_recipe', args=[recipe.id]),
                                                                                                          request.user.get_full_name())
                    send_mail(subject, '', 
                              'bramspammer@seasoning.be',
                              ['bram@seasoning.be'], fail_silently=False, html_message=message)
            
            if incomplete:
                recipe = get_object_or_404(IncompleteRecipe, id=recipe_id)
            else:
                recipe = get_object_or_404(Recipe, id=recipe_id)
                
            resp_txt = ''
            if len(form.changed_data) > 0:
                if form.changed_data[0] == 'extra_info' or form.changed_data[0] == 'description':
                    resp_txt = defaultfilters.linebreaks(getattr(recipe, form.changed_data[0]))
                if form.changed_data[0] == 'instructions':
                    resp_txt = markdown(getattr(recipe, form.changed_data[0]))
            elif ing_formset.has_changed():
                ing_formset = UsesIngredientFormset(instance=recipe)
                resp_txt = render_to_string('includes/edit_ingredients_list.html', {'ing_formset': ing_formset})
                
            return HttpResponse(resp_txt)
        
        print(form.errors)
        print(ing_formset.errors)
        if form.errors:
            return HttpResponseServerError(form.errors[form.changed_data[0]])
        else:
            return HttpResponseServerError(ing_formset.errors[0].values()[0])
        
    raise PermissionDenied()

def ajax_browse_recipes(request):
    if request.method == 'POST' and request.is_ajax():
        # This is a formset for inputting ingredients to be included or excluded in the recipe search
        IngredientInRecipeFormset = formset_factory(IngredientInRecipeSearchForm, extra=1)
    
        page = 1
        search_form = SearchRecipeForm(request.POST)
        
        include_ingredients_formset = IngredientInRecipeFormset(request.POST, prefix='include')
        exclude_ingredients_formset = IngredientInRecipeFormset(request.POST, prefix='exclude')
        
        recipes_list = []
        if search_form.is_valid() and include_ingredients_formset.is_valid() and exclude_ingredients_formset.is_valid():
            data = search_form.cleaned_data
            include_ingredient_names = [form.cleaned_data['name'] for form in include_ingredients_formset if 'name' in form.cleaned_data]
            exclude_ingredient_names = [form.cleaned_data['name'] for form in exclude_ingredients_formset if 'name' in form.cleaned_data]
            recipes_list = Recipe.objects.query(search_string=data['search_string'], advanced_search=data['advanced_search'],
                                                sort_field=data['sort_field'], inseason=data['inseason'], ven=data['ven'], 
                                                veg=data['veg'], nveg=data['nveg'], cuisines=data['cuisine'], courses=data['course'], 
                                                include_ingredients_operator=data['include_ingredients_operator'],
                                                include_ingredient_names=include_ingredient_names, exclude_ingredient_names=exclude_ingredient_names)
        page = search_form.cleaned_data.get('page', 1)
        
        # Split the result by 12
        paginator = Paginator(recipes_list, 12, allow_empty_first_page=False)
        
        try:
            recipes = paginator.page(page)
        except PageNotAnInteger:
            recipes = paginator.page(1)
        except EmptyPage:
            raise Http404(search_form.errors)
        
        search_form_id = 'recipe-search-form'
    
        return render(request, 'includes/recipe_summaries.html', {'recipes': recipes,
                                                                  'search_form_id': search_form_id})
        
    raise PermissionDenied()

@login_required
def ajax_upload_recipe_image(request, recipe_id):
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        upload_image_form = UploadRecipeImageForm(request.POST, request.FILES)
        
        if upload_image_form.is_valid():
            image = upload_image_form.save(commit=False)
            image.recipe = recipe
            image.added_by = request.user
            image.save()
            
            return HttpResponse(json.dumps({'url': image.image.url,
                                            'image_id': image.id}))
    
    raise PermissionDenied()

@login_required
@csrf_exempt
def ajax_finish_recipe_image(request, recipe_image_id):
    if request.method == 'POST':
        if 'x' in request.POST and 'y' in request.POST and 'w' in request.POST and 'h' in request.POST:
            recipe_image = get_object_or_404(RecipeImage, id=recipe_image_id)
            
            recipe_image.x = request.POST['x']
            recipe_image.y = request.POST['y']
            recipe_image.w = request.POST['w']
            recipe_image.h = request.POST['h']
            
            recipe_image.visible = True
            recipe_image.save()
            
            return HttpResponse(0)
    
    raise PermissionDenied()    