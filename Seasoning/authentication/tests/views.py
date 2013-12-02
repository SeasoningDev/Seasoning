from django.test import TestCase
from django.conf import settings
from authentication.forms import RegistrationForm, ResendActivationEmailForm,\
    AccountSettingsForm, DeleteAccountForm, CheckActiveAuthenticationForm
from authentication.models import User, RegistrationProfile, NewEmail
import datetime
import os
from django.core import mail
from django.contrib.sites.models import Site
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django_dynamic_fixture import G

class AccountViewsTestCase(TestCase):
    
    def setUp(self):
        self.user = G(User, is_active=True)
        self.user.set_password('test')
        self.user.save()
    
    def test_login(self):
        resp = self.client.get('/login/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertEqual(resp.context['form'].__class__, CheckActiveAuthenticationForm)
        
        resp = self.client.post('/login/', {'username': self.user.email,
                                            'password': 'test'})
        self.assertRedirects(resp, '/', 302, 200)
        
        resp = self.client.post('/login/', {'username': self.user.email,
                                            'password': 'test',
                                            'next': '/login/'})
        self.assertRedirects(resp, '/login/', 302, 200)
        
        # Bad input
        resp = self.client.post('/login/', {})
        self.assertEqual(resp.status_code, 200)
    
    def test_public_profile(self):
        location = '/profile/%d/' % self.user.pk
        resp = self.client.get(location)
        # Need to be logged in first
        self.assertRedirects(resp, '/login/?next=' + location, 302, 200)
        
        resp = self.client.post('/login/', {'username': self.user.email,
                                            'password': 'test'})
        resp = self.client.get(location)
        
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('viewed_user' in resp.context)
        self.assertTrue(resp.context['viewed_user'].pk == self.user.pk)
        self.assertTrue('recipes' in resp.context)
        for recipe in resp.context['recipes']:
            self.assertTrue(recipe.author == self.user.pk)
    
    def test_account_settings(self):
        location = '/profile/'
        resp = self.client.get(location)
        # Need to be logged in first
        self.assertRedirects(resp, '/login/?next=' + location, 302, 200)
        
        resp = self.client.post('/login/', {'username': self.user.email,
                                            'password': 'test'})
        resp = self.client.get(location)
        
    
    def test_account_settings_profile(self):
        location = '/account/settings/profile/'
        resp = self.client.get(location)
        # Need to be logged in first
        self.assertRedirects(resp, '/login/?next=' + location, 302, 200)
        
        resp = self.client.post('/login/', {'username': self.user.email,
                                            'password': 'test'})
        resp = self.client.get(location)
        
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertEqual(resp.context['form'].__class__, AccountSettingsForm)
        self.assertFalse('new_email' in resp.context)
        
        # Bad input
        resp = self.client.post(location, {})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(self.user.new_emails.all()), 0)
        self.assertFalse('new_email' in resp.context)
        
        resp = self.client.post(location, {'givenname': self.user.givenname,
                                           'surname': self.user.surname,
                                           'email': self.user.email + 'extra'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(self.user.new_emails.all()), 1)
        self.assertTrue('new_email' in resp.context)
        
    
    def test_account_settings_social(self):
        location = '/account/settings/social/'
        resp = self.client.get(location)
        # Need to be logged in first
        self.assertRedirects(resp, '/login/?next=' + location, 302, 200)
        
        resp = self.client.post('/login/', {'username': self.user.email,
                                            'password': 'test'})
        resp = self.client.get(location)
        
    
    def test_account_settings_privacy(self):
        location = '/account/settings/privacy/'
        resp = self.client.get(location)
        # Need to be logged in first
        self.assertRedirects(resp, '/login/?next=' + location, 302, 200)
        
        resp = self.client.post('/login/', {'username': self.user.email,
                                            'password': 'test'})
        resp = self.client.get(location)
        
    
    def test_change_email(self):
        location = '/email/change/'
        resp = self.client.get(location + 'aaa/')
        # Need to be logged in first
        self.assertRedirects(resp, '/login/?next=%saaa/' % location, 302, 200)
        
        resp = self.client.post('/login/', {'username': self.user.email,
                                            'password': 'test'})
        
        # If no new email is present, 404
        resp = self.client.get(location + 'aaa/')
        self.assertEqual(resp.status_code, 404)
        
        # Change user email
        resp = self.client.post('/account/settings/profile/', {'givenname': self.user.givenname,
                                                               'surname': self.user.surname,
                                                               'email': self.user.email + 'extra'})
        # Wrong key should 404
        resp = self.client.get(location + 'aaa/')
        self.assertEqual(resp.status_code, 404)
        
        new_email = self.user.new_emails.all()[0]
        resp = self.client.get(location + '%s/' % new_email.activation_key)
        self.assertRedirects(resp, '/profile/', 302, 200)
        
    
    def test_change_password(self):
        location = '/password/change/'
        resp = self.client.get(location)
        # Need to be logged in first
        self.assertRedirects(resp, '/login/?next=' + location, 302, 200)
        
        resp = self.client.post('/login/', {'username': self.user.email,
                                            'password': 'test'})
        
        resp = self.client.get(location)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertEqual(resp.context['form'].__class__, PasswordChangeForm)
        
        resp = self.client.post(location, {'old_password': 'test',
                                           'new_password1': 'test',
                                           'new_password2': 'test'})
        self.assertRedirects(resp, '/profile/', 302, 200)
        
        # Bad input
        resp = self.client.post(location, {})
        self.assertEqual(resp.status_code, 200)
        
        self.user.password = '!'
        self.user.save()
        resp = self.client.get(location)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertEqual(resp.context['form'].__class__, SetPasswordForm)
        
        resp = self.client.post(location, {'new_password1': 'test',
                                           'new_password2': 'test'})
        self.assertRedirects(resp, '/profile/', 302, 200)
    
    def test_account_delete(self):
        location = '/account/delete/'
        resp = self.client.get(location)
        # Need to be logged in first
        self.assertRedirects(resp, '/login/?next=' + location, 302, 200)
        
        resp = self.client.post('/login/', {'username': self.user.email,
                                            'password': 'test'})
        resp = self.client.get(location)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertEqual(resp.context['form'].__class__, DeleteAccountForm)
        
        # Bad input
        resp = self.client.post(location, {})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.get(pk=self.user.pk), self.user)
        
        resp = self.client.post(location, {'checkstring': 'DELETEME'})
        self.assertRedirects(resp, '/', 302, 200)
        self.assertRaises(User.DoesNotExist, lambda: User.objects.get(pk=self.user.pk))
       
class RegistrationViewsTestCase(TestCase):
    
    def setUp(self):
        self.old_allowed = getattr(settings, 'REGISTRATION_OPEN', True)
        self.registration_info = {'givenname': 'test',
                                  'surname': 'user',
                                  'password': 'haha',
                                  'password2': 'haha',
                                  'email': 'testuser@test.be',
                                  'date_of_birth': datetime.date.today(),
                                  'tos': True,
                                  'recaptcha_response_field': 'PASSED'}
        
    def tearDown(self):
        # Reset registration open
        settings.REGISTRATION_OPEN = self.old_allowed
    
    def test_register(self):
        # Test registration disallowed
        settings.REGISTRATION_OPEN = False

        resp = self.client.get('/register/')
        self.assertRedirects(resp, 'register/closed/', 302, 200)
        
        # From now on, only test with registration allowed
        settings.REGISTRATION_OPEN = True
        
        resp = self.client.get('/register/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertEqual(resp.context['form'].__class__, RegistrationForm)
        
        resp = self.client.post('/register/', {'givenname': 'test',
                                               'surname': 'user',
                                               'password': 'haha',
                                               'password2': 'hahaa',
                                               'email': 'testuser@test.be',
                                               'date_of_birth': datetime.date.today(),
                                               'tos': False,
                                               'captcha': ''})
        # Invalid information in the form should just display the same page
        self.assertEqual(resp.status_code, 200)
        
        os.environ['RECAPTCHA_TESTING'] = 'True'
        resp = self.client.post('/register/', self.registration_info)
        
        # Valid information in the form should redirect to registration complete
        self.assertRedirects(resp, 'register/complete/', 302, 200)
        self.assertEqual(len(mail.outbox), 1)
        User.objects.get(email='testuser@test.be')
    
    def test_registration_closed(self):
        resp = self.client.get('/register/closed/')
        self.assertEqual(resp.status_code, 200)
    
    def test_registration_complete(self):
        resp = self.client.get('/register/complete/')
        self.assertEqual(resp.status_code, 200)
    
    def test_resend_activation_email(self):
        settings.REGISTRATION_OPEN = True
        os.environ['RECAPTCHA_TESTING'] = 'True'
        # Register a user
        self.client.post('/register/', self.registration_info)
        
        resp = self.client.get('/activate/resend/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertEqual(resp.context['form'].__class__, ResendActivationEmailForm)
        
        # Unknown email
        resp = self.client.post('/activate/resend/', {'email': self.registration_info['email'] + 'extra'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        
        resp = self.client.post('/activate/resend/', {'email': self.registration_info['email']})
        self.assertRedirects(resp, '/', 302, 200)
        self.assertEqual(len(mail.outbox), 2)        
    
    def test_activate(self):
        settings.REGISTRATION_OPEN = True
        os.environ['RECAPTCHA_TESTING'] = 'True'
        # Register a user
        self.client.post('/register/', self.registration_info)
        
        registration_profile = RegistrationProfile.objects.get(user=User.objects.get(email=self.registration_info['email']))
        
        # Bad activation key
        resp = self.client.get('/activate/%s%s/' % (registration_profile.activation_key, 'extra'))
        self.assertEqual(resp.status_code, 404)
        self.failIf(User.objects.get(email=self.registration_info['email']).is_active)
        
        # Correct activation key
        resp = self.client.get('/activate/%s/' % registration_profile.activation_key)
        self.assertRedirects(resp, '/', 302, 200)
        self.assertTrue(User.objects.get(email=self.registration_info['email']).is_active)
