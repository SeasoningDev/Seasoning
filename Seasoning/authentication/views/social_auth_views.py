import base64
from authentication.backends import GoogleAuthBackend, FacebookAuthBackend
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import redirect, render
from authentication.models import User
from django.contrib import messages
from general.views import home
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from authentication.forms import SocialRegistrationForm
from django.core.exceptions import PermissionDenied

BACKENDS = {'google': GoogleAuthBackend,
            'fb': FacebookAuthBackend}

def base64_url_decode(inp):
    padding_factor = len(inp) % 4
    inp += "="*padding_factor
    return base64.b64decode(unicode(inp).translate(dict(zip(map(ord, u'-_'), u'+/'))))

def social_auth(request, backend):
    backend = BACKENDS[backend]
    backend = backend()
    
    error = request.GET.get('error', None)
    code = request.GET.get('code', None)
    state = request.GET.get('state', None)
    next_page = state or request.REQUEST.get('next', None)
    
    if error is not None:
        # Something went wrong
        error_reason = request.GET.get(backend.ERROR_REASON_PARAM, '')
        if error_reason == backend.ACCESS_DENIED_STRING:
            # User denied us access to his profile...
            messages.add_message(request, messages.INFO, _('Could not access your ' + backend.name() + ' Information. Please try again.'))            
            return redirect('/login/')
        else:
            messages.add_message(request, messages.INFO, _('Something went wrong. Check URL for error.'))
            return render(request, 'authentication/login.html')
            
    redirect_uri = 'http://' + str(get_current_site(request)) + '/auth/' + backend.NAME + '/'
    if code is None:
        # User has just click the 'Login with ...' button to start a social authentication.
        # Redirect him to the social network, so we may get an authorization code.
        return redirect(backend.get_auth_code_url(redirect_uri=redirect_uri, 
                                                  next_page=next_page))
    else:
        # User has been redirected to the social network, and has come back with a code
        # We now need to exchange this code for an access token in our backend
        access_token = backend.get_access_token(code,
                                                redirect_uri=redirect_uri)
    
        if access_token:
            # We now have an access token
            try:
                user_info = backend.get_user_info(access_token)
            except PermissionDenied:
                messages.add_message(request, messages.INFO, _('You cannot use this type of ' + backend.name() + ' account on Seasoning. Please try another...'))            
                return redirect('/login/')
            
            if user_info:
                # We received a valid access token, and were able to exchange it for the necessary
                # user information. 
                # Lets try to authenticate the user
                user = authenticate(**{backend.ID_FIELD: user_info['id']})
                
                if user:
                    # User was successfully authenticated, so log him in
                    auth_login(request, user)
                    return redirect(next_page or home)
                # A user with the this id whas not found in the database. Check if we can find a
                # Seasoning account with the social users email
                try:
                    user = User.objects.get(email=user_info['email'])
                    # A user with the given email has been found. Prompt the user to
                    # connect his social network account to his Seasoning account
                    messages.add_message(request, messages.INFO, _('The email corresponding to your ' + backend.name() + ' account is already in use on Seasoning. '
                                                                   'If this account belongs to you, please log in to connect it to your ' + backend.name() + ' account, '
                                                                   'otherwise, please contact an administrator.'))
                    # The user is probably not logged in at this point, so he will be asked to log
                    # in first before connecting his social network account to his Seasoning account.
                    return redirect(backend.connect_url)
                except User.DoesNotExist:
                    # A user with the given email was not found. Prompt the user to register
                    # at Seasoning using his social network account
                    messages.add_message(request, messages.INFO, _('Your ' + backend.name() + ' account has not been connected to Seasoning yet. Please take a minute to register.'))
                    return redirect(backend.registration_url)
    
    # The code or access token was not correct or we were unable to connect to the social network. Please try again later
    messages.add_message(request, messages.INFO, _('An error occurred while checking your identity with ' + backend.name() + '. Please try again.'))
    return redirect('/login/')

@login_required
def social_connect(request, backend):
    backend = BACKENDS[backend]
    backend = backend()
    
    if request.method == 'POST':
        # The user has posted his intent to connect his social network id with
        # his Seasoning account
        access_token = request.POST.get('access-token', '')
        if access_token:
            # Check the access token and get the users Social info
            try:
                user_info = backend.get_user_info(access_token)
            except PermissionDenied:
                messages.add_message(request, messages.INFO, _('You cannot connect this type of ' + backend.name() + ' account to your Seasoning account. Please try another...'))            
                return redirect('/login/')
            if user_info:
                # Access token was valid and we have received the users' info
                # Check if this user is already connected to a Seasoning account
                user = authenticate(**{backend.ID_FIELD: user_info['id']})
                if user:
                    # User already has an account on Seasoning, so we can't connect it to another one
                    messages.add_message(request, messages.INFO, _('This ' + backend.name() + ' account is already connected to another account.'))
                else:
                    backend.connect_user(request.user, user_info['id'])
                    messages.add_message(request, messages.INFO, _('Your ' + backend.name() + ' account has been successfully connected to your Seasoning account!'))
                    return redirect(home)
            else:
                # Invalid access token or something else went wrong
                messages.add_message(request, messages.INFO, _('An error occurred while checking your identity with ' + backend.name() + '. Please try again.'))
    
    # User wants to connect his social account to his Seasoning account. Get the neccessary information
    # He either did something wrong while posting his response, or has not had the change to post it yet.
    error = request.GET.get('error', None)
    code = request.GET.get('code', None)
    access_token = request.GET.get('accessToken', None)
    next_page = request.REQUEST.get('next', None)
    
    if error is not None:
        # Something went wrong
        error_reason = request.GET.get(backend.ERROR_REASON_PARAM, '')
        if error_reason == backend.ACCESS_DENIED_STRING:
            # User denied us access to his profile...
            messages.add_message(request, messages.INFO, _('Could not access your ' + backend.name() + ' Information. Please try again.'))            
            return redirect('/account/settings/social/')
        else:
            messages.add_message(request, messages.INFO, _('Something went wrong. Check URL for error.'))
            return render(request, 'authentication/login.html')
            
    redirect_uri = 'http://' + str(get_current_site(request)) + backend.connect_url
    if code is None:
        # Redirect User to the social network, so we may get an authorization code.
        return redirect(backend.get_auth_code_url(redirect_uri=redirect_uri, 
                                                  next_page=next_page))
    else:
        # User has been redirected to the social network, and has come back with a code
        # We now need to exchange this code for an access token in our backend
        access_token = backend.get_access_token(code,
                                                redirect_uri=redirect_uri)
    
        if access_token:
            # We now have an access token
            try:
                user_info = backend.get_user_info(access_token)
            except PermissionDenied:
                messages.add_message(request, messages.INFO, _('You cannot connect this type of ' + backend.name() + ' account to your Seasoning account. Please try another...'))            
                return redirect('/login/')
            
            if user_info:
                # We received a valid access token, and were able to exchange it for the necessary
                # user information.
                context = {'backend': backend,
                           'access_token': access_token}
                context.update(user_info)
                return render(request, 'authentication/social_connect.html', context)
        
        messages.add_message(request, messages.INFO, _('An error occurred while checking your identity with ' + backend.name() + '. Please try again.'))
        return redirect('/profile/')
    
@login_required
def social_disconnect(request, backend):
    backend = BACKENDS[backend]
    backend = backend()
    
    if request.user.password == '!' and not (request.user.google_id and request.user.facebook_id):
        # The user does not have both social account connected, and has not set his password. If he disconnects this
        # social network, he will not be able to log in
        messages.add_message(request, messages.INFO, _('You can only disconnect your ' + backend.name() + ' account if your password has been set.'))
    else:
        backend.disconnect_user(request.user)
        messages.add_message(request, messages.INFO, _('Your Seasoning account has been disconnected from your ' + backend.name() + ' account.'))
    return redirect('/profile/')


@csrf_exempt
def social_register(request, backend, disallowed_url='registration_disallowed'):
    backend = BACKENDS[backend]
    backend = backend()
    
    if request.method == 'POST':
        # The user has posted a registration request
        # The access token will provide us with the information from the users' social network account
        access_token = request.POST.get('access_token', None)
        # The form data will provide us with additional information
        form = SocialRegistrationForm(request.POST)
        if form.is_valid():
            # User agreed to tos, and if he provided password, they match
            if access_token:
                # We also need to check if the additional information provided by the user is valid
                try:
                    user_info = backend.get_user_info(access_token)
                except PermissionDenied:
                    messages.add_message(request, messages.INFO, _('You cannot use this type of ' + backend.name() + ' account to register on Seasoning. Please try another...'))            
                    return redirect('/register/')
                if user_info:
                    try:
                        # Check if a user with this social id already exists
                        User.objects.get(**{backend.ID_FIELD: user_info['id']})
                        messages.add_message(request, messages.INFO, _('A user has already registered with your ' + backend.name() + ' account. If this is you, please log in, otherwise, contact an administrator'))
                        return redirect('/login/')
                    except User.DoesNotExist:
                        pass
                    try:
                        # Check if a user with this Facebook email is already registered
                        User.objects.get(email=user_info['email'])
                        messages.add_message(request, messages.INFO, _('A user has already registered on Seasoning with the email in your ' + backend.name() + '. If this is your account, would you like to connect it to your ' + backend.name() + 'account?'))
                        return redirect(backend.connect_url)
                    except User.DoesNotExist:
                        # A user with this Google email does not exist, so we will register a new one
                        pass
                    
                    # Check if registration is allowed
                    if not backend.registration_allowed(request):
                        return redirect(disallowed_url)
                    # Register the user
                    password = form.cleaned_data['password'] or None
                    user = backend.register(request, social_id=user_info['id'], givenname=user_info['givenname'], 
                                            surname=user_info['surname'], email=user_info['email'], 
                                            date_of_birth=user_info['date_of_birth'], password=password)
                    # And log him in, because we don't need to validate his information
                    user = authenticate(**{backend.ID_FIELD: user_info['id']})
                    auth_login(request, user)
                    messages.add_message(request, messages.INFO, _('You have successfully registered your ' + backend.name() + ' account on Seasoning. Have fun!'))            
                    return redirect(home)
                # If we're here, we had a faulty access token. Set the access token to None so as not to get caught in the if condition below and display the error
                # message as expected
                access_token = None
    else:
        # User wants to register using his social account
        code = request.GET.get('code', None)
        
        redirect_uri = 'http://' + str(get_current_site(request)) + backend.registration_url
        if code is None:
            # User has just click the 'Register with ...' button to start a social registration.
            # Redirect him to the social network, so we may get an authorization code.
            return redirect(backend.get_auth_code_url(redirect_uri=redirect_uri))
        else:
            # User has been redirected to the social network, and has come back with a code
            # We now need to exchange this code for an access token in our backend
            form = SocialRegistrationForm()
        
            access_token = backend.get_access_token(code,
                                                    redirect_uri=redirect_uri)
    if access_token:
        # We now have an access token either by getting one with an authorization code, or by extracting it from the
        # POST parameters
        try:
            user_info = backend.get_user_info(access_token)
        except PermissionDenied:
            messages.add_message(request, messages.INFO, _('You cannot use this type of ' + backend.name() + ' account to register on Seasoning. Please try another...'))            
            return redirect('/register/')
        
        try:
            # Check if a user with this social id already exists
            User.objects.get(**{backend.ID_FIELD: user_info['id']})
            messages.add_message(request, messages.INFO, _('A user has already registered with your ' + backend.name() + ' account. If this is you, please log in, otherwise, contact an administrator'))
            return redirect('/login/')
        except User.DoesNotExist:
            pass
        try:
            # Check if a user with this Facebook email is already registered
            User.objects.get(email=user_info['email'])
            messages.add_message(request, messages.INFO, _('A user has already registered on Seasoning with the email in your ' + backend.name() + '. If this is your account, please log in to connect it to your ' + backend.name() + ' account?'))
            return redirect(backend.connect_url)
        except User.DoesNotExist:
            # A user with this Google email does not exist, so we will register a new one
            pass
                    
                    
        
        context = {'backend': backend,
                   'form': form,
                   'access_token': access_token}
        context.update(user_info)
        if user_info:
            return render(request, 'authentication/social_register.html', context)
                    
    # If we're here, something above must have gone wrong...
    messages.add_message(request, messages.INFO, _('An error occurred while checking your identity with ' + backend.name() + '. Please try again.'))
    return redirect(backend.registration_url)