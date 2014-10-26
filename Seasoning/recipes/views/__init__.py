from std import *
from ajax import *
from admin import *

from django.contrib.comments.signals import comment_was_posted

# Inform user when posting a comment was succesfull
def comment_posted_message(sender, comment=None, request=None, **kwargs):
    messages.add_message( request, messages.SUCCESS, 'Uw reactie werd succesvol toegevoegd.' )
comment_was_posted.connect(comment_posted_message)

import os
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib.formtools.wizard.views import SessionWizardView
from django.utils.decorators import method_decorator
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django import forms
from django.contrib.formtools.wizard.forms import ManagementForm
from general.forms import FormContainer
from recipes.models import UnknownIngredient
from recipes.forms import EditRecipeBasicInfoForm,\
    EditRecipeIngredientsForm, EditRecipeInstructionsForm
from ingredients.models import CanUseUnit

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
            if (self.request.user.id != self.instance.author_id) and not self.request.user.is_staff:
                raise PermissionDenied()
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
            new_recipe = True
        else:
            new_recipe = False
        # recipe has not been saved yet
        self.instance.save()
        
        if new_recipe:
            done_message = 'Je nieuwe recept werd met succes toegevoegd!'
        else:
            done_message = 'Je recept werd met succes aangepast!'
        
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
                                CanUseUnit(ingredient=ingredient, unit=ingredient_info['unit'], conversion_factor=0).save()
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
                                  'ingredientenaanvraag@seasoning.be',
                                  ['info@seasoning.be'], fail_silently=True)
                        
                        done_message += '\nOmdat je ingredienten hebt aangevraagd, zal je recept echter pas zichtbaar zijn voor andere gebruikers wanneer deze ingredienten aan de databank toegevoegd zijn.'
            
                    ing_form.save()
                        
                    # And save the recipe again to update the footprint
                    recipe = Recipe.objects.select_related().prefetch_related('uses__unit').get(pk=self.instance.pk)
                    recipe.save()
        
        messages.add_message(self.request, messages.INFO, done_message)
        return redirect('/recipes/%d/' % self.instance.id)


"""
Ajax calls
"""


"""
Unused for now

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
                interval_count = 20
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
"""


@login_required
def delete_recipe_comment(request, recipe_id, comment_id):
    comment = get_object_or_404(comments.get_model(), pk=comment_id)
    if comment.user == request.user:
        perform_delete(request, comment)
        messages.add_message(request, messages.INFO, 'Je reactie werd succesvol verwijderd.')
        return redirect(view_recipe, recipe_id)
    else:
        raise PermissionDenied()