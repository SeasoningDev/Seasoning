from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from authentication.forms import AccountSettingsForm, DeleteAccountForm,\
    CheckActiveAuthenticationForm
from authentication.models import NewEmail, User
from django.contrib import messages
from django.contrib.sites.models import RequestSite
from django.shortcuts import render, redirect
from django.http.response import Http404
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.views import login as django_login, logout
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.aggregates import Avg, Count

def login(request):
    return django_login(request, template_name='authentication/login.html', 
                        authentication_form=CheckActiveAuthenticationForm)

@login_required
def account_settings(request, user_id=None):
    viewing_self = False
    try:
        if user_id is None or user_id == request.user.id:
            user = get_user_model().objects.prefetch_related('recipes').get(id=request.user.id)
            viewing_self = True
        else:
            user = get_user_model().objects.prefetch_related('recipes').get(id=user_id)
    except get_user_model().DoesNotExist:
        raise Http404
    recipes_list = user.recipes.all().order_by('-rating')
    
    try:
        averages = user.recipes.all().aggregate(Avg('footprint'), Avg('rating'))
        most_used_veganism = max(user.recipes.values('veganism').annotate(dcount=Count('veganism')), key=lambda i: i['dcount'])['veganism']
    except ValueError:
        averages = {'footprint__avg': None,
                    'rating__avg': None}
        most_used_veganism = None
    
    # Split the result by 9
    paginator = Paginator(recipes_list, 9)
    
    page = request.GET.get('page')
    try:
        recipes = paginator.page(page)
    except PageNotAnInteger:
        recipes = paginator.page(1)
    except EmptyPage:
        recipes = paginator.page(paginator.num_pages)
    
    if request.is_ajax():
        return render(request, 'includes/recipe_summaries.html', {'recipes': recipes})
    
    return render(request, 'authentication/account_settings.html', {'viewed_user': user,
                                                                    'viewing_other': not viewing_self,
                                                                    'recipes': recipes,
                                                                    'average_fp': 4*averages['footprint__avg'],
                                                                    'average_rating': averages['rating__avg'],
                                                                    'most_used_veganism': most_used_veganism})

@login_required
def account_settings_profile(request):
    """
    Allow a user to change his account settings
    
    If the user has changed his email address, an activation email will be sent to this new
    address. The new address will not be activated until the link in this email has been
    clicked.
    
    If the user has an alternate email that should be activated, this will also be displayed
    on this page.
    
    """
    context = {}
    user = get_user_model().objects.get(id=request.user.id)
    if request.method == "POST":
        form = AccountSettingsForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            if form.new_email is not None:
                # Send an activation email to the new email
                NewEmail.objects.create_inactive_email(user, form.new_email, RequestSite(request))
                messages.add_message(request, messages.INFO, _('An email has been sent to the new email address provided by you. Please follow the instructions '
                                                               'in this email to complete the changing of your email address.'))
            # New email address has been replaced by old email address in the form, so it will not be saved until activated
            form.save()
            user = get_user_model().objects.get(id=request.user.id)
    else:
        form = AccountSettingsForm(instance=user)
    
    try:
        new_email = NewEmail.objects.get(user=request.user)
        context['new_email'] = new_email.email
    except NewEmail.DoesNotExist:
        pass
    
    context['form'] = form
    context['user'] = user
    return render(request, 'authentication/account_settings_profile.html', context)

@login_required
def account_settings_social(request):
    return render(request, 'authentication/account_settings_social.html')

@login_required
def account_settings_privacy(request):
    return render(request, 'authentication/account_settings_privacy.html')

@login_required
def change_email(request, activation_key):
    """
    This checks if the given activation key belongs to the current users new,
    inactive email address. If so, this new email address is activated, and
    the users old email address is deleted.
    
    """
    activated = NewEmail.objects.activate_email(request.user, activation_key)
    if activated:
        messages.add_message(request, messages.INFO, _('Your email address has been successfully changed.'))
        return redirect(account_settings)
    raise Http404

@sensitive_post_parameters()
@login_required
def change_password(request,
                    template_name='authentication/password_change_form.html',
                    password_change_form=PasswordChangeForm):
    """
    Provides a form where the users password can be changed.
    
    """
    if request.user.password == '!':
        password_change_form = SetPasswordForm
        
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, _('Your password has been successfully changed.'))
            return redirect(account_settings)
    
    form = password_change_form(user=request.user)
    return render(request, template_name, {'form': form})

@login_required
def account_delete(request):
    """
    Provides a method for deleting the users account
    
    """
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            user = User.objects.get(pk=request.user.id)
            logout(request)
            user.delete()
            return redirect('/')
    else:
        form = DeleteAccountForm()
    return render(request, 'authentication/account_delete.html', {'form': form})
