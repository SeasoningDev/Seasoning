"""
Copyright 2012, 2013 Driesen Joep

This file is part of Seasoning.

Seasoning is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Seasoning is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Seasoning.  If not, see <http://www.gnu.org/licenses/>.
    
"""
from django.shortcuts import render, redirect, get_object_or_404
from recipes.models import Recipe, Vote, UsesIngredient, UnknownIngredient
from recipes.forms import AddRecipeForm, UsesIngredientForm, SearchRecipeForm,\
    IngredientInRecipeSearchForm, EditRecipeBasicInfoForm,\
    EditRecipeIngredientsForm, EditRecipeInstructionsForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied,\
    ValidationError
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory
from django.contrib import messages, comments
from django.db.models import Q
from ingredients.models import Ingredient
from django.forms.formsets import formset_factory
from django.contrib.comments.views.moderation import perform_delete
from general.views import home
from django.http.response import Http404, HttpResponse
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
import json
from django.core.serializers.json import DjangoJSONEncoder
from recipes.forms import IngredientsFormSet
from django.core.mail import send_mail
import datetime
import ingredients
from django.db.models.aggregates import Max, Min
from django.contrib.formtools.wizard.views import SessionWizardView
from django.utils.decorators import method_decorator
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from django import forms
from general.forms import FormContainer
from django.contrib.formtools.wizard.forms import ManagementForm
from ingredients.models import Unit

def browse_recipes(request):
    """
    Browse or search through recipes
    
    """
    # This is a formset for inputting ingredients to be included or excluded in the recipe search
    IngredientInRecipeFormset = formset_factory(IngredientInRecipeSearchForm, extra=1)
    
    if request.method == 'POST':
        search_form = SearchRecipeForm(request.POST)
        try:
            include_ingredients_formset = IngredientInRecipeFormset(request.POST, prefix='include')
            exclude_ingredients_formset = IngredientInRecipeFormset(request.POST, prefix='exclude')
            if search_form.is_valid() and include_ingredients_formset.is_valid() and exclude_ingredients_formset.is_valid():
                data = search_form.cleaned_data
                include_ingredient_names = [form.cleaned_data['name'] for form in include_ingredients_formset if 'name' in form.cleaned_data]
                exclude_ingredient_names = [form.cleaned_data['name'] for form in exclude_ingredients_formset if 'name' in form.cleaned_data]
                recipes_list = Recipe.objects.query(search_string=data['search_string'], advanced_search=data['advanced_search'],
                                                    sort_field=data['sort_field'], sort_order=data['sort_order'], ven=data['ven'], 
                                                    veg=data['veg'], nveg=data['nveg'], cuisines=data['cuisine'], courses=data['course'], 
                                                    include_ingredients_operator=data['include_ingredients_operator'],
                                                    include_ingredient_names=include_ingredient_names, exclude_ingredient_names=exclude_ingredient_names)
            else:
                recipes_list = []
        except ValidationError:
            # A simple search with only the recipe name was done (from the homepage)
            search_form.is_valid()
            if 'search_string' in search_form.cleaned_data:
                recipes_list = Recipe.objects.filter(name__icontains=search_form.cleaned_data['search_string'], accepted=True).order_by('footprint')
            else:
                recipes_list = []
            search_form = SearchRecipeForm()
            include_ingredients_formset = IngredientInRecipeFormset(prefix='include')
            exclude_ingredients_formset = IngredientInRecipeFormset(prefix='exclude')
            
    else:
        search_form = SearchRecipeForm()
        include_ingredients_formset = IngredientInRecipeFormset(prefix='include')
        exclude_ingredients_formset = IngredientInRecipeFormset(prefix='exclude')
        recipes_list = Recipe.objects.query()
    
    # Split the result by 12
    paginator = Paginator(recipes_list, 12)
    
    page = request.GET.get('page')
    try:
        recipes = paginator.page(page)
    except PageNotAnInteger:
        recipes = paginator.page(1)
    except EmptyPage:
        recipes = paginator.page(paginator.num_pages)
    
    if request.method == 'POST' and request.is_ajax():
        return render(request, 'includes/recipe_summaries.html', {'recipes': recipes})
        
    return render(request, 'recipes/browse_recipes.html', {'search_form': search_form,
                                                           'include_ingredients_formset': include_ingredients_formset,
                                                           'exclude_ingredients_formset': exclude_ingredients_formset,
                                                           'recipes': recipes})

def view_recipe(request, recipe_id):
    
    recipe = Recipe.objects.select_related('author', 'cuisine').get(pk=recipe_id)
    usess = UsesIngredient.objects.select_related('ingredient', 'unit').filter(recipe=recipe).order_by('-group', 'ingredient__name')
    
    user_vote = None
    if request.user.is_authenticated():
        try:
            user_vote = Vote.objects.get(recipe_id=recipe_id, user=request.user)
        except ObjectDoesNotExist:
            pass
    
    total_time = recipe.active_time + recipe.passive_time
    active_time_perc = (float(recipe.active_time) / total_time) * 100
    passive_time_perc = 100 - active_time_perc
    
    comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Recipe), object_pk=recipe.id, is_removed=False, is_public=True).select_related('user')
    
    return render(request, 'recipes/view_recipe.html', {'recipe': recipe,
                                                        'usess': usess,
                                                        'user_vote': user_vote,
                                                        'active_time_perc': active_time_perc,
                                                        'passive_time_perc': passive_time_perc,
                                                        'total_time': total_time,
                                                        'comments': comments})

class EditRecipeWizard(SessionWizardView):
    
    FORMS = [('basic_info', EditRecipeBasicInfoForm),
             ('ingredients', EditRecipeIngredientsForm),
             ('instructions', EditRecipeInstructionsForm)]
    
    TEMPLATES = {'basic_info': 'recipes/edit_recipe_basic_info.html',
                 'ingredients': 'recipes/edit_recipe_ingredients.html',
                 'instructions': 'recipes/edit_recipe_instructions.html'}
    
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'tmp_recipe_imgs'))
    
    instance = None
    
    def get_form_instance(self, step):
        return self.instance

    def get_form(self, step=None, data=None, files=None):
        """
        We need to overwrite this, because otherwise 'instance' is not passed
        to the FormContainer
        
        """
        if step is None:
            step = self.steps.current
        # prepare the kwargs for the form instance.
        kwargs = self.get_form_kwargs(step)
        kwargs.update({
            'data': data,
            'files': files,
            'prefix': self.get_form_prefix(step, self.form_list[step]),
            'initial': self.get_form_initial(step),
        })
        if issubclass(self.form_list[step], forms.ModelForm) or issubclass(self.form_list[step], FormContainer):
            # If the form is based on ModelForm, add instance if available
            # and not previously set.
            kwargs.setdefault('instance', self.get_form_instance(step))
        elif issubclass(self.form_list[step], forms.models.BaseModelFormSet) or issubclass(self.form_list[step], FormContainer):
            # If the form is based on ModelFormSet, add queryset if available
            # and not previous set.
            kwargs.setdefault('queryset', self.get_form_instance(step))
        return self.form_list[step](**kwargs)
    
    def form_is_valid(self, step=None):
        if step is None:
            step = self.steps.current
        
        form = self.get_form(step=step, data=self.storage.get_step_data(step),
                             files=self.storage.get_step_files(step))
        if not form.is_bound:
            # The form did not receive any new data. It can only be valid if an instance was present
            return self.instance is not None and self.instance.id is not None
        
        # The form received new data, check the validity of the new data
        return form.is_valid()
    
    def is_valid(self):
        return all(self.form_is_valid(step) for step in self.steps.all)            
        
    def get_template_names(self):
        return self.TEMPLATES[self.steps.current]
    
    def get_context_data(self, form, **kwargs):
        context = SessionWizardView.get_context_data(self, form, **kwargs)
        # Check if we are adding a new or editing an existing recipe
        if 'recipe_id' in self.kwargs:
            context['new_recipe'] = False
        else:
            context['new_recipe'] = True
        for step in self.steps.all:
            context['%s_form_valid' % step] = self.form_is_valid(step)
        return context
    
    # Make sure login is required for every view in this class
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if 'recipe_id' in self.kwargs:
            try:
                self.instance = Recipe.objects.select_related().prefetch_related('uses__unit').get(pk=self.kwargs['recipe_id'])
            except Recipe.DoesNotExist:
                raise Http404
            if (not self.request.user == self.instance.author_id) and not self.request.user.is_staff:
                raise PermissionDenied
        else:
            self.instance = Recipe()
        return SessionWizardView.dispatch(self, *args, **kwargs)

    def post(self, *args, **kwargs):
        """
        This method handles POST requests.

        The wizard will render either the current step (if form validation
        wasn't successful), the next step (if the current step was stored
        successful and the next step was requested) or the done view (if no 
        more steps are available or the entire wizard was submitted)
        """
        # Look for a wizard_goto_step element in the posted data which
        # contains a valid step name. If one was found, render the requested
        # form. (This makes stepping back a lot easier).
        wizard_goto_step = self.request.POST.get('wizard_goto_step', None)
        wizard_finish = self.request.POST.get('wizard_finish', None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            self.storage.current_step = wizard_goto_step
            form = self.get_form(
                data=self.storage.get_step_data(self.steps.current),
                files=self.storage.get_step_files(self.steps.current))
            form.is_valid()
            return self.render(form)

        # Check if form was refreshed
        management_form = ManagementForm(self.request.POST, prefix=self.prefix)
        if not management_form.is_valid():
            raise ValidationError('ManagementForm data is missing or has been tampered.')

        form_current_step = management_form.cleaned_data['current_step']
        if (form_current_step != self.steps.current and
                self.storage.current_step is not None):
            # form refreshed, change current step
            self.storage.current_step = form_current_step

        # get the form for the current step
        form = self.get_form(data=self.request.POST, files=self.request.FILES)

        # and try to validate
        if form.is_valid():
            # if the form is valid, store the cleaned data and files.
            self.storage.set_step_data(self.steps.current, self.process_step(form))
            self.storage.set_step_files(self.steps.current, self.process_step_files(form))
            
            if wizard_finish:
                # User tried to submit the entire form
                if self.is_valid():
                    return self.render_done(form, **kwargs)
                else:
                    for step in self.steps.all:
                        if not self.form_is_valid(step):
                            self.storage.current_step = step
                            form = self.get_form(step=step, data=self.storage.get_step_data(step),
                                                 files=self.storage.get_step_files(step))
                            form.is_valid()
                            return self.render(form)
                
            # check if the current step is the last step
            if self.steps.current == self.steps.last:
                # no more steps, render done view
                return self.render_done(form, **kwargs)
            else:
                # proceed to the next step
                return self.render_next_step(form)
        
        return self.render(form)

    def render_next_step(self, form, **kwargs):
        """
        This method gets called when the next step/form should be rendered.
        `form` contains the last/current form.
        """
        # get the form instance based on the data from the storage backend
        # (if available).
        next_step = self.steps.next
        
        data = self.storage.get_step_data(next_step)
        files = self.storage.get_step_files(next_step)
        
        new_form = self.get_form(next_step, data=data, files=files)
        
        if data or files:
            new_form.is_valid()
        
        # change the stored current step
        self.storage.current_step = next_step
        return self.render(new_form, **kwargs)

    def render_done(self, form, **kwargs):
        """
        This method gets called when all forms passed. The method should also
        re-validate all steps to prevent manipulation. If any form don't
        validate, `render_revalidation_failure` should get called.
        If everything is fine call `done`.
        """
        final_form_list = []
        # walk through the form list and try to validate the data again.
        for form_key in self.get_form_list():
            form_obj = self.get_form(step=form_key,
                data=self.storage.get_step_data(form_key),
                files=self.storage.get_step_files(form_key))
            if form_obj.is_bound or self.instance is None or self.instance.id is None:
                # only add the form if it changes the instances attributes
                if not form_obj.is_valid():
                    return self.render_revalidation_failure(form_key, form_obj, **kwargs)
                final_form_list.append(form_obj)

        # render the done view and reset the wizard before returning the
        # response. This is needed to prevent from rendering done with the
        # same data twice.
        done_response = self.done(final_form_list, **kwargs)
        self.storage.reset()
        return done_response
    
    def done(self, form_list, **kwargs):
        if not self.instance.author:
            self.instance.author = self.request.user
        # recipe has not been saved yet
        self.instance.save()
        
        # Check if the ingredients form is present
        for form in form_list:
            if hasattr(form, 'forms') and 'ingredients' in form.forms:
                ing_form = form.forms['ingredients']
                if ing_form.has_changed():
                    # Check for unknown ingredients
                    if ing_form.unknown_ingredients:
                        request_string = ''
                        for ingredient_info in ing_form.unknown_ingredients:
                            request_string += 'Naam ingredient: %s\nGevraagde eenheid: %s\n\n' % (ingredient_info['name'], ingredient_info['unit'])
                            try:
                                ingredient = Ingredient.objects.with_name(ingredient_info['name'])
                                # If this works, the ingredient exists, but isn't accepted
                            except Ingredient.DoesNotExist:
                                # An ingredient with the given name does not exist, so we need to add it
                                ingredient = Ingredient(name=ingredient_info['name'], category=Ingredient.DRINKS, base_footprint=0)
                                ingredient.save()
                            if not ingredient.can_use_unit(ingredient_info['unit']):
                                ingredients.models.CanUseUnit(ingredient=ingredient, unit=ingredient_info['unit'], conversion_factor=0).save()
                            if not UnknownIngredient.objects.filter(name=ingredient_info['name'], requested_by=self.request.user, real_ingredient=ingredient, for_recipe=self.instance).exists():
                                UnknownIngredient(name=ingredient_info['name'], requested_by=self.request.user, real_ingredient=ingredient, for_recipe=self.instance).save()
                        
                        # revalidate the ingredient forms
                        for form in ing_form:
                            # Allow unaccepted ingredients this time around
                            form.fields['ingredient'].unaccepted_ingredients_allowed = True
                            form.full_clean()
                        
                        # Send mail
                        send_mail('Aanvraag voor Ingredienten', render_to_string('emails/request_ingredients_email.txt', {'user': self.request.user,
                                                                                                                          'request_string': request_string}), 
                                  self.request.user.email,
                                  ['info@seasoning.be'], fail_silently=True)
            
                    ing_form.save()
                        
                    # And save the recipe again to update the footprint
                    recipe = Recipe.objects.select_related().prefetch_related('uses__unit').get(pk=self.instance.pk)
                    recipe.save()
        
        messages.add_message(self.request, messages.INFO, 'Je nieuwe recept werd met succes toegevoegd!')
        return redirect('/recipes/%d/' % self.instance.id)

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
    

"""
Ajax calls
"""

@csrf_exempt
@login_required
def vote(request):
    
    if request.is_ajax() and request.method == 'POST':
        recipe_id = request.POST.get('recipe', None)
        score = request.POST.get('score', None)
        
        if recipe_id and score:
            try:
                recipe = Recipe.objects.select_related().get(pk=recipe_id)
            except Recipe.DoesNotExist:
                raise Http404
            recipe.vote(user=request.user, score=int(score))
            data = simplejson.dumps({'new_rating': recipe.rating,
                                     'new_novotes': recipe.number_of_votes})
            return HttpResponse(data)
        
    raise PermissionDenied
    

@csrf_exempt
@login_required
def remove_vote(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    recipe.unvote(user=request.user)

@csrf_exempt
def get_recipe_portions(request):
    
    if request.is_ajax() and request.method == 'POST':
        recipe_id = request.POST.get('recipe', None)
        portions = request.POST.get('portions', None)
        
        if recipe_id is not None and portions is not None and portions > 0:
            try:
                recipe = Recipe.objects.get(pk=recipe_id)
                usess = UsesIngredient.objects.select_related('ingredient', 'unit').filter(recipe=recipe).order_by('group', 'ingredient__name')
            except Recipe.DoesNotExist, UsesIngredient.DoesNotExist:
                raise Http404
            
            ratio = float(portions)/recipe.portions
            new_footprint = ratio * recipe.total_footprint()
            
            for uses in usess:
                uses.save_allowed = False
                uses.amount = ratio * uses.amount
                uses.footprint = ratio * uses.footprint
            
            data = {'ingredient_list': render_to_string('includes/ingredient_list.html', {'usess': usess}),
                    'new_footprint': new_footprint}
            json_data = simplejson.dumps(data)
            
            return HttpResponse(json_data)
    
    raise PermissionDenied

@csrf_exempt
def get_recipe_footprint_evolution(request):
    
    if request.is_ajax() and request.method == 'POST':
        recipe_id = request.POST.get('recipe', None)
    
        if recipe_id is not None:
            try:
                recipe = Recipe.objects.get(pk=recipe_id)
                usess = UsesIngredient.objects.select_related('ingredient', 'unit__parent_unit').prefetch_related('ingredient__available_in_country', 'ingredient__available_in_sea', 'ingredient__canuseunit_set__unit__parent_unit').filter(recipe=recipe).order_by('group', 'ingredient__name')
                # One footprint per month
                footprints = [0] * 12
                dates = [datetime.date(day=1, month=month, year=ingredients.models.AvailableIn.BASE_YEAR) for month in range(1, 13)]
                for uses in usess:
                    for i in range(12):
                        footprints[i] += uses.normalized_footprint(uses.ingredient.footprint(date=dates[i]))
                footprints = [float('%.2f' % (4*footprint/recipe.portions)) for footprint in footprints]
                footprints.append(footprints[-1])
                footprints.insert(0, footprints[0])
                data = {'footprints': footprints,
                        'doy': datetime.date.today().timetuple().tm_yday}
                json_data = simplejson.dumps(data)
            
                return HttpResponse(json_data)
            except Recipe.DoesNotExist, UsesIngredient.DoesNotExist:
                raise Http404
        
    raise PermissionDenied

@csrf_exempt
def get_relative_footprint(request):
    
    if request.is_ajax() and request.method == 'POST':
        recipe_id = request.POST.get('recipe', None)
    
        if recipe_id is not None:
            try:
                recipe = Recipe.objects.get(pk=recipe_id)
                bounds = Recipe.objects.aggregate(Max('footprint'), Min('footprint'))
                min_fp = 4*bounds['footprint__min']
                max_fp = 4*bounds['footprint__max']
                interval_count = 10
                interval_length = (max_fp-min_fp)/interval_count
                recipes = Recipe.objects.values('footprint', 'course', 'veganism').all().order_by('footprint')
                
                intervals = [min_fp+i*interval_length for i in range(interval_count+1)]
                all_footprints = []
                category_footprints = []
                veganism_footprints = []
                
                footprint_index = 0
                for upper_bound in intervals[1:]:
                    # Don't check the first value in the intervals, because we only need upper bounds
                    # of intervals
                    all_footprints.append(0)
                    category_footprints.append(0)
                    veganism_footprints.append(0)
                    while 4*recipes[footprint_index]['footprint'] <= upper_bound:
                        all_footprints[-1] += 1
                        if recipe.course == recipes[footprint_index]['course']:
                            category_footprints[-1] += 1
                        if recipe.veganism == recipes[footprint_index]['veganism']:
                            veganism_footprints[-1] += 1
                        footprint_index += 1
                        if footprint_index >= len(recipes):
                            break
                data = {'all_fps': all_footprints,
                        'cat_fps': category_footprints,
                        'veg_fps': veganism_footprints,
                        'min_fp': min_fp,
                        'max_fp': max_fp,
                        'interval_length': interval_length,
                        'fp': 4*recipe.footprint}
                json_data = simplejson.dumps(data)
            
                return HttpResponse(json_data)
            
            except Recipe.DoesNotExist:
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
        data = simplejson.dumps({unit['id']: unit['name'] for unit in units})
        return HttpResponse(data)
    raise PermissionDenied()

def ajax_markdown_preview(request):
    if request.method == 'POST' and request.is_ajax():
        markdown = request.POST.get('data', '')
        return render(request, 'recipes/markdown_preview.html', {'markdown_text': markdown})
    raise PermissionDenied()
