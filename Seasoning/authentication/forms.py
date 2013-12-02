from authentication.models import User
from captcha.fields import ReCaptchaField
from django import forms
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.forms.models import ModelForm
from django.forms.widgets import ClearableFileInput
from django.utils.html import format_html
from django.template import loader
from django.utils.http import int_to_base36
from django.contrib.sites.models import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.core.mail.message import EmailMultiAlternatives
from django.conf import settings

        
class ShownImageInput(ClearableFileInput):
    """
    This is a custom Form field that shows a thumbnail of the current image above
    the file input field
    
    """
    initial_text = _(' ')
    
    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = '%(input)s'
        substitutions['input'] = super(ClearableFileInput, self).render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = format_html('<img src="{0}">',
                                                   value.url)

        return mark_safe(template % substitutions)

class RegistrationForm(forms.ModelForm):
    """
    Form for registering a new user account.
    
    Adds a ReCaptcha field and a required checkbox for agreeing to the 
    site's Terms of Service. 
    
    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.
    
    """
    class Meta:
        model = User
        fields = ['givenname', 'surname', 'password', 'email', 'date_of_birth']
    
    givenname = forms.CharField(max_length=30,
                                widget=forms.TextInput(attrs={'tabindex':'1'}),
                                help_text=_('30 characters or fewer, only letters allowed. '
                                            'Your name will be used to identify you on Seasoning.'))
    
    surname = forms.CharField(max_length=50,
                              widget=forms.TextInput(attrs={'tabindex':'2'}),
                              help_text=_('50 characters or fewer, only letters allowed '
                                          'Your name will be used to identify you on Seasoning.'))
    
    email = forms.EmailField(widget=forms.TextInput(attrs={'tabindex':'3'}),
                             help_text=_('Your email will never be sold or shared. It will not be shown on the site, unless you enable this '
                                         'option.<br/>An email will be sent to this email address to verify your account. You will not '
                                         'receive any further emails from Seasoning.'))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'required',
                                                                 'tabindex': '4'}, render_value=False))
    
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'required',
                                                                  'tabindex': '5'}, render_value=False),
                                label=_("Password (again)"),
                                help_text=_('Please enter the same password as above for verification purposes.'))
    
    date_of_birth = forms.DateField(widget=forms.TextInput(attrs={'tabindex':'6'}),
                                    input_formats=['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y'],
                                    help_text=_('Your birthday will be used for age validation and possible some anonymous statistics about the '
                                                'users of Seasoning.'))
                             
    captcha = ReCaptchaField(attrs={'theme': 'red',
                                    'tabindex': 7},
                             error_messages = {'required': _("You must enter the correct ReCaptcha characters")})
    
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'required',
                                                               'tabindex': '8'}),
                             label=mark_safe(_(u'I have read and agree to the <a target="_blank" href="/terms/">Terms of Service</a>')),
                             error_messages={'required': _("You must agree to the terms to register")})
    
    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        super(RegistrationForm, self).clean()
        if 'password' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data

attrs_dict = {'class': 'required',
              'tabindex': '8'}

class SocialRegistrationForm(forms.Form):
    """
    This form is used for registering users using a social network. The passwords
    are optional
    
    """
    
    password = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password"), required=False) 
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password (again)"), required=False)
    
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})
    
    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        super(SocialRegistrationForm, self).clean()
        if 'password' in self.cleaned_data or 'password2' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data

    
class ResendActivationEmailForm(forms.Form):
    """
    Form for resending an activation email to a user.
    
    The user must enter an email address to which he would like to have a
    new activation email sent. If the email address does not correspond to
    an inactive account, and error is returned
    
    If the given email address does correspond to an inactive account, the 
    cleaned email field will contain the registration profile of the account.
    
    """    
    email = forms.EmailField(label="E-mail", max_length=75, required=False,
                             error_messages = {'invalid': _("Please enter a valid email address"),
                                               'required': _("Please enter a valid email address")})
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            raise forms.ValidationError(_("The given email address was not found"))
        
        if user.is_active:
            raise forms.ValidationError(_("The account corresponding to this email address has already been activated"))
        
        profile = user.registrationprofile
        if profile.activation_key_expired():
            raise forms.ValidationError(_("The account corresponding to this email address has expired due to prolonged inactivity"))
            
        return profile
        
    

class CheckActiveAuthenticationForm(AuthenticationForm):
    """
    This form is used instead of the standard authentication form. It customizes
    the error message returned when the used has not been ativated yet.
    
    """    
    def __init__(self, *args, **kwargs):
        super(CheckActiveAuthenticationForm, self).__init__(*args, **kwargs)
        self.error_messages['inactive'] = mark_safe(_('This account has not been activated yet, so you may not log in at '
                                                      'this time. If you haven\'t received an activation email for 15 minutes '
                                                      'after registering, you can use <a href=\"/activate/resend/\">this form</a> '
                                                      'to resend an activation email.'))
        
class AccountSettingsForm(ModelForm):
    """
    This form allows a user to change his account settings
    
    If the user enters a new email address, the form will get an attribute 'new_email'
    with the new email address as its value. Otherwise this attribute will be None.
    
    The cleaned email will revert to the old email address of the user because the new
    email address must be activated before it is saved.
    
    """    
    class Meta:
        model = get_user_model()
        fields = ['givenname', 'surname', 'email', 'avatar']
        widgets = {
            'avatar': ShownImageInput,
        }
    
    def __init__(self, *args, **kwargs):
        super(AccountSettingsForm, self).__init__(*args, **kwargs)
        if self.instance.name_changed:
            del self.fields['givenname']
            del self.fields['surname']
        
    def clean_email(self):
        user = self.instance
        new_email = self.cleaned_data['email']
        if not user.email == new_email:
            self.new_email = new_email
        else:
            self.new_email = None
        self.cleaned_data['email'] = user.email
        return user.email

class DeleteAccountForm(forms.Form):
    """
    This form provides a fail-safe when a user tries to delete his account. The user
    will have to provide a string 'DELETEME' if he really wants to delete his account.
    Additionally the user will have to check if he would like to delete all his
    added recipes.
    
    """
    checkstring = forms.CharField()
    delete_recipes = forms.BooleanField(required=False)
    
    def clean_checkstring(self):
        checkstring = self.cleaned_data['checkstring']
        if not checkstring == 'DELETEME':
            raise forms.ValidationError('You must provide the string \'DELETEME\' if you would like to delete your account')
        return checkstring

class MultiEmailPasswordResetForm(PasswordResetForm):
    
    def save(self, domain_override=None,
             subject_template_name='authentication/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.pk),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            subject = loader.render_to_string('authentication/password_reset_subject.txt', c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            message_text = loader.render_to_string('authentication/password_reset_email.txt', c)
            message_html = loader.render_to_string('authentication/password_reset_email.html', c)            
            

            msg = EmailMultiAlternatives(subject, message_text, settings.DEFAULT_FROM_EMAIL, [self.user.email])
            msg.attach_alternative(message_html, "text/html")
            msg.send()