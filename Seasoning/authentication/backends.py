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
from django.contrib.auth import login, load_backend
from django.conf import settings
from authentication import signals
from authentication.forms import RegistrationForm
from authentication.models import RegistrationProfile, User
from django.contrib.auth.backends import ModelBackend
import urllib2
from django.utils import simplejson
from urllib2 import HTTPError
import urllib
import datetime
from django.core.exceptions import PermissionDenied
from django.contrib.sites.models import RequestSite


class RegistrationBackend(object):
    """
    A registration backend which follows a simple workflow:

    1. User signs up, inactive account is created.

    2. Email is sent to user with activation link.

    3. User clicks activation link, account is now active.

    Using this backend requires that

    * ``registration`` be listed in the ``INSTALLED_APPS`` setting
      (since this backend makes use of models defined in this
      application).

    * The setting ``ACCOUNT_ACTIVATION_DAYS`` be supplied, specifying
      (as an integer) the number of days from registration during
      which a user may activate their account (after that period
      expires, activation will be disallowed).

    * The creation of the templates
      ``authentication/activation_email_subject.txt`` and
      ``authentication/activation_email.txt``, which will be used for
      the activation email. See the notes for this backends
      ``register`` method for details regarding these templates.

    Additionally, registration can be temporarily closed by adding the
    setting ``REGISTRATION_OPEN`` and setting it to
    ``False``. Omitting this setting, or setting it to ``True``, will
    be interpreted as meaning that registration is currently open and
    permitted.

    Internally, this is accomplished via storing an activation key in
    an instance of ``registration.models.RegistrationProfile``. See
    that model and its custom manager for full documentation of its
    fields and supported operations.
    
    """
    def register(self, request, **kwargs):
        """
        Given a givenname, surname, email address, password and date of
        birth, register a new user account, which will initially be inactive.

        Along with the new ``User`` object, a new
        ``registration.models.RegistrationProfile`` will be created,
        tied to that ``User``, containing the activation key which
        will be used for this account.

        An email will be sent to the supplied email address; this
        email should contain an activation link. The email will be
        rendered using two templates. See the documentation for
        ``RegistrationProfile.send_activation_email()`` for
        information about these templates and the contexts provided to
        them.

        After the ``User`` and ``RegistrationProfile`` are created and
        the activation email is sent, the signal
        ``registration.signals.user_registered`` will be sent, with
        the new ``User`` as the keyword argument ``user`` and the
        class of this backend as the sender.

        """
        givenname, surname, email, password, date_of_birth = kwargs['givenname'], kwargs['surname'], kwargs['email'], kwargs['password'],  kwargs['date_of_birth']
        
        site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(givenname, surname, email,
                                                                    password, date_of_birth, 
                                                                    site)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user
    
    def activate(self, request, activation_key):
        """
        Given an an activation key, look up and activate the user
        account corresponding to that key (if possible).

        After successful activation, the signal
        ``registration.signals.user_activated`` will be sent, with the
        newly activated ``User`` as the keyword argument ``user`` and
        the class of this backend as the sender.
        
        """
        activated = RegistrationProfile.objects.activate_user(activation_key)
        if activated:
            signals.user_activated.send(sender=self.__class__,
                                        user=activated,
                                        request=request)
            # Bit of an ugly hack to get around authentication
            backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
            activated.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            login(request, activated)
        return activated
    
    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.
        
        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def get_form_class(self, request):
        """
        Return the default form class used for user registration.
        
        """
        return RegistrationForm

    def post_registration_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        user registration.
        
        """
        return ('registration_complete', (), {})

    def post_activation_redirect(self, request, user):
        """
        Return the name of the URL to redirect to after successful
        account activation.

        """
        return ('activation_complete', (), {})

class OAuth2Backend(ModelBackend):
    
    ID_FIELD = None
    NAME = None
    OAUTH_URL = None
    TOKEN_REQUEST_URL = None
    USER_INFO_URL = None
    APP_ID = None
    APP_SECRET = None
    SCOPE = None
    ERROR_REASON_PARAM = None
    ACCESS_DENIED_STRING = None
    
    def name(self):
        if self.NAME is None:
            raise NotImplementedError
        return self.NAME.capitalize()
    
    @property
    def connect_url(self):
        return '/auth/' + self.NAME + '/connect/'
    
    @property
    def registration_url(self):
        return '/auth/' + self.NAME + '/register/'
    
    def authenticate(self, **kwargs):
        if self.ID_FIELD is None:
            raise NotImplementedError
        if not self.ID_FIELD in kwargs:
            raise TypeError
        social_id = kwargs[self.ID_FIELD]
        try:
            return User.objects.get(**{self.ID_FIELD: social_id})
        except User.DoesNotExist:
            return None
    
    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.
        
        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def register(self, request, social_id, givenname, surname, email, date_of_birth, password=None):
        if self.ID_FIELD is None:
            raise NotImplementedError
        new_user = User.objects.create_user(givenname, surname, email, date_of_birth, password)
        setattr(new_user, self.ID_FIELD, social_id)
        new_user.save()
        
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
    
    def get_auth_code_url(self, redirect_uri, next_page=None):
        if self.APP_ID is None or self.SCOPE is None or self.OAUTH_URL is None:
            raise NotImplementedError
        params = ['response_type=code',
                  'client_id=' + self.APP_ID,
                  'redirect_uri=' + redirect_uri,
                  'scope=' + self.SCOPE]
        if next_page:
            params.append('state='+ next_page)
        return self.OAUTH_URL + '?' + '&'.join(params)
    
    def get_unparsed_user_info(self, access_token):
        try:
            user_info = urllib2.urlopen(self.USER_INFO_URL + '?access_token=' + access_token)
            return simplejson.loads(user_info.read())
        except HTTPError:
            return False
    
    def connect_user(self, user, social_id):
        if self.ID_FIELD is None:
            raise NotImplementedError
        setattr(user, self.ID_FIELD, social_id)
        user.save()
    
    def disconnect_user(self, user):
        if self.ID_FIELD is None:
            raise NotImplementedError
        setattr(user, self.ID_FIELD, None)
        user.save()
    
    
class GoogleAuthBackend(OAuth2Backend):
    
    ID_FIELD = 'google_id'
    NAME = 'google'
    OAUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_REQUEST_URL = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
    APP_ID = settings.GOOGLE_APP_ID
    APP_SECRET = settings.GOOGLE_SECRET
    SCOPE = 'https://www.googleapis.com/auth/userinfo.email+https://www.googleapis.com/auth/userinfo.profile'
    ERROR_REASON_PARAM = 'error'
    ACCESS_DENIED_STRING = 'access_denied'
    
    def get_access_token(self, code, redirect_uri):
        if self.APP_ID is None or self.APP_SECRET is None or self.TOKEN_REQUEST_URL is None:
            raise NotImplementedError
        try:
            post_data = {'code': code,
                         'client_id': self.APP_ID,
                         'client_secret': self.APP_SECRET,
                         'redirect_uri': redirect_uri,
                         'grant_type': 'authorization_code'}
            data = urllib.urlencode(post_data)
            token_response = urllib2.urlopen(self.TOKEN_REQUEST_URL, data)
            try:
                token = simplejson.loads(token_response.read())
                return token['access_token']
            except (KeyError, ValueError):
                error = TypeError()
                error.token_response = token_response.read()
                raise error
        except HTTPError:
            return None
    
    def get_user_info(self, access_token):
        google_info = self.get_unparsed_user_info(access_token)
        try:
            date_of_birth = datetime.datetime.strptime(google_info['birthday'], '%Y-%m-%d').date()
        except (ValueError, KeyError):
            date_of_birth = datetime.date.today()
        return {'id': google_info['id'],
                'name': google_info['name'],
                'givenname': google_info['given_name'],
                'surname': google_info['family_name'],
                'email': google_info['email'],
                'date_of_birth': date_of_birth,
                'image': 'http://profiles.google.com/s2/photos/profile/' + google_info['id'] + '?sz=100'}
    
    
class FacebookAuthBackend(OAuth2Backend):
    
    ID_FIELD = 'facebook_id'
    NAME = 'fb'
    OAUTH_URL = 'https://www.facebook.com/dialog/oauth'
    TOKEN_REQUEST_URL = 'https://graph.facebook.com/oauth/access_token'
    USER_INFO_URL = 'https://graph.facebook.com/me'
    APP_ID = settings.FACEBOOK_APP_ID
    APP_SECRET = settings.FACEBOOK_SECRET
    SCOPE = 'email,user_birthday'
    ERROR_REASON_PARAM = 'error_reason'
    ACCESS_DENIED_STRING = 'user_denied'
    
    def name(self):
        return 'Facebook'
    
    def get_access_token(self, code, redirect_uri):
        try:
            params = {'code=' + code,
                      'client_id=' + self.APP_ID,
                      'client_secret=' + self.APP_SECRET,
                      'redirect_uri=' + redirect_uri,}
            full_token_request_url = self.TOKEN_REQUEST_URL + '?' + '&'.join(params)
            fb_token_response = urllib2.urlopen(full_token_request_url).read()
            return fb_token_response.replace('access_token=', '')
        except HTTPError:
            return None
    
    def get_user_info(self, access_token):
        fb_info = self.get_unparsed_user_info(access_token)
        try:
            date_of_birth = datetime.datetime.strptime(fb_info['birthday'], '%m/%d/%Y').date()
        except ValueError:
            date_of_birth = datetime.date.today()
        try:
            return {'id': fb_info['id'],
                    'name': fb_info['name'],
                    'givenname': fb_info['first_name'],
                    'surname': fb_info['last_name'],
                    'email': fb_info['email'],
                    'date_of_birth': date_of_birth,
                    'image': 'https://graph.facebook.com/' + fb_info['id'] + '/picture'}
        except KeyError:
            raise PermissionDenied
    
    