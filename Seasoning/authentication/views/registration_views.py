from django.http.response import Http404
from general.views import home
from django.contrib import messages
from django.shortcuts import redirect, render, render_to_response
from authentication.forms import ResendActivationEmailForm
from django.contrib.sites.models import RequestSite
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

def register(request, backend, success_url=None, form_class=None,
             disallowed_url='registration_disallowed',
             template_name='authentication/registration_form.html',
             extra_context=None):
    """
    Allow a new user to register an account.

    The actual registration of the account will be delegated to the
    backend specified by the ``backend`` keyword argument (see below);
    it will be used as follows:

    1. The backend's ``registration_allowed()`` method will be called,
       passing the ``HttpRequest``, to determine whether registration
       of an account is to be allowed; if not, a redirect is issued to
       the view corresponding to the named URL pattern
       ``registration_disallowed``. To override this, see the list of
       optional arguments for this view (below).

    2. The form to use for account registration will be obtained by
       calling the backend's ``get_form_class()`` method, passing the
       ``HttpRequest``. To override this, see the list of optional
       arguments for this view (below).

    3. If valid, the form's ``cleaned_data`` will be passed (as
       keyword arguments, and along with the ``HttpRequest``) to the
       backend's ``register()`` method, which should return the new
       ``User`` object.

    4. Upon successful registration, the backend's
       ``post_registration_redirect()`` method will be called, passing
       the ``HttpRequest`` and the new ``User``, to determine the URL
       to redirect the user to. To override this, see the list of
       optional arguments for this view (below).
    
    **Required arguments**
    
    None.
    
    **Optional arguments**

    ``backend``
        The backend class to use.

    ``disallowed_url``
        URL to redirect to if registration is not permitted for the
        current ``HttpRequest``. Must be a value which can legally be
        passed to ``django.shortcuts.redirect``. If not supplied, this
        will be whatever URL corresponds to the named URL pattern
        ``registration_disallowed``.
    
    ``form_class``
        The form class to use for registration. If not supplied, this
        will be retrieved from the registration backend.
    
    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context.

    ``success_url``
        URL to redirect to after successful registration. Must be a
        value which can legally be passed to
        ``django.shortcuts.redirect``. If not supplied, this will be
        retrieved from the registration backend.
    
    ``template_name``
        A custom template to use. If not supplied, this will default
        to ``authentication/registration_form.html``.
    
    **Context:**
    
    ``form``
        The registration form.
    
    Any extra variables supplied in the ``extra_context`` argument
    (see above).
    
    **Template:**
    
    authentication/registration_form.html or ``template_name`` keyword
    argument.
    
    """
    if request.user.is_authenticated():
        messages.add_message(request, messages.INFO, _('You already have an account!'))
        return redirect('/')
    
    backend = backend()
    if not backend.registration_allowed(request):
        return redirect(disallowed_url)
    if form_class is None:
        form_class = backend.get_form_class(request)
    
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = backend.register(request, **form.cleaned_data)
            if success_url is None:
                to, args, kwargs = backend.post_registration_redirect(request, new_user)
                return redirect(to, *args, **kwargs)
            else:
                return redirect(success_url)
    else:
        form = form_class()
        
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    
    return render_to_response(template_name,
                              {'form': form},
                              context_instance=context)

def registration_closed(request):
    return render(request, 'authentication/registration_closed.html')
    
def registration_complete(request):
    return render(request, 'authentication/registration_complete.html')
    

def resend_activation_email(request):
    """
    Allow a registered, non-activated user to resend an activation email.
    
    The user will be required to provide the non-activated email address. After
    checking if this email address indeed corresponds to a non-activated account,
    an email will be sent to it. 
    
    """
    if request.method == "POST":
        
        form = ResendActivationEmailForm(data=request.POST)
        
        if form.is_valid():
            site = RequestSite(request)
            
            # Send an activation email to the registration profile corresponding to the
            # given email
            form.cleaned_data['email'].send_activation_email(site)
            
            messages.add_message(request, messages.INFO, _('A new activation email has been sent to %s. This email should '
                                                           'arrive within 15 minutes. Please be sure to check your Spam/Junk '
                                                           'folder.'))
            return redirect(home)
        
    else:
        form = ResendActivationEmailForm()
        
    return render(request, 'authentication/resend_activation_email.html', {'form': form})


def activate(request, backend, **kwargs):
    """
    Activate a user's account.

    The actual activation of the account will be delegated to the
    backend specified by the ``backend`` keyword argument (see below);
    the backend's ``activate()`` method will be called, passing any
    keyword arguments captured from the URL, and will be assumed to
    return a ``User`` if activation was successful, or a value which
    evaluates to ``False`` in boolean context if not.

    Upon successful activation, the user will be redirected to the home
    page and displayed a message that the activation was succesfull.

    **Arguments**

    ``backend``
        The backend class to use. Required.

    ``**kwargs``
        Any keyword arguments captured from the URL, such as an
        activation key, which will be passed to the backend's
        ``activate()`` method.
    
    """
    backend = backend()
    account = backend.activate(request, **kwargs)

    if account:
        messages.add_message(request, messages.INFO, _('Your account has been successfully activated. Have fun!'))            
        return redirect(home)
    return render(request, 'authentication/activate_unsuccessfull.html')

