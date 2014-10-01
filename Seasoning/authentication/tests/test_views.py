import datetime
import os
from django.test import TestCase
from django.conf import settings
from django.core import mail
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django_dynamic_fixture import G
from authentication.forms import RegistrationForm, ResendActivationEmailForm,\
    AccountSettingsForm, DeleteAccountForm, CheckActiveAuthenticationForm
from authentication.models import User, RegistrationProfile
from django.core.urlresolvers import reverse

class AccountViewsTestCase(TestCase):
    
    def setUp(self):
        self.user = G(User, is_active=True)
        self.user.set_password('test')
        self.user.save()
        
    def check_login_required_and_login(self, location):
        resp = self.client.get(location)
        # Need to be logged in first
        self.assertRedirects(resp, reverse('login') + '?next=' + location, 302, 200)
        
        return self.client.post(reverse('login'), {'username': self.user.email,
                                                   'password': 'test',
                                                   'next': location})
    
    def test_login(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertEqual(resp.context['form'].__class__, CheckActiveAuthenticationForm)
        
        resp = self.client.post(reverse('login'), {'username': self.user.email,
                                                   'password': 'test'})
        self.assertRedirects(resp, '/', 302, 200)
        
        resp = self.client.post(reverse('login'), {'username': self.user.email,
                                                   'password': 'test',
                                                   'next': reverse('login')})
        self.assertRedirects(resp, reverse('login'), 302, 200)
        
        # Bad input
        resp = self.client.post(reverse('login'), {})
        self.assertEqual(resp.status_code, 200)
    
    def test_public_profile(self):
        location = reverse('user_profile', args=(self.user.pk,))
        self.check_login_required_and_login(location)
        
        resp = self.client.get(location)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('viewed_user' in resp.context)
        self.assertTrue(resp.context['viewed_user'].pk == self.user.pk)
    
    def test_account_settings(self):
        location = reverse('my_profile')
        self.check_login_required_and_login(location)
        
    
    def test_account_settings_profile(self):
        location = reverse('account_settings')
        self.check_login_required_and_login(location)
        
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
        location = reverse('account_settings_social')
        self.check_login_required_and_login(location)
        
    
    def test_account_settings_privacy(self):
        location = reverse('account_settings_privacy')
        self.check_login_required_and_login(location)
        
    
    def test_change_email(self):
        location = reverse('change_email', args=('aaa',))
        self.check_login_required_and_login(location)
        
        resp = self.client.get(location)
        self.assertEqual(resp.status_code, 404)
        
        # Change user email
        resp = self.client.post(reverse('account_settings'), {'givenname': self.user.givenname,
                                                              'surname': self.user.surname,
                                                              'email': self.user.email + 'extra'})
        # Wrong key should 404
        resp = self.client.get(location)
        self.assertEqual(resp.status_code, 404)
        
        new_email = self.user.new_emails.all()[0]
        
        location = reverse('change_email', args=(new_email.activation_key,))
        resp = self.client.get(location)
        self.assertRedirects(resp, reverse('my_profile'), 302, 200)
        
    
    def test_change_password(self):
        location = reverse('password_change')
        self.check_login_required_and_login(location)

        resp = self.client.get(location)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertEqual(resp.context['form'].__class__, PasswordChangeForm)
        
        resp = self.client.post(location, {'old_password': 'test',
                                           'new_password1': 'test',
                                           'new_password2': 'test'})
        self.assertRedirects(resp, reverse('my_profile'), 302, 200)
        
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
        self.assertRedirects(resp, reverse('my_profile'), 302, 200)
    
    def test_account_delete(self):
        location = reverse('delete_profile')
        self.check_login_required_and_login(location)
        
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

        resp = self.client.get(reverse('registration'))
        self.assertRedirects(resp, reverse('registration_disallowed'), 302, 200)
        
        # From now on, only test with registration allowed
        settings.REGISTRATION_OPEN = True
        
        resp = self.client.get(reverse('registration'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertEqual(resp.context['form'].__class__, RegistrationForm)
        
        resp = self.client.post(reverse('registration'), {'givenname': 'test',
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
        resp = self.client.post(reverse('registration'), self.registration_info)
        
        # Valid information in the form should redirect to registration complete
        self.assertRedirects(resp, reverse('registration_complete'), 302, 200)
        self.assertEqual(len(mail.outbox), 1)
        User.objects.get(email='testuser@test.be')
    
    def test_registration_closed(self):
        resp = self.client.get(reverse('registration_disallowed'))
        self.assertEqual(resp.status_code, 200)
    
    def test_registration_complete(self):
        resp = self.client.get(reverse('registration_complete'))
        self.assertEqual(resp.status_code, 200)
    
    def test_resend_activation_email(self):
        settings.REGISTRATION_OPEN = True
        os.environ['RECAPTCHA_TESTING'] = 'True'
        # Register a user
        self.client.post(reverse('registration'), self.registration_info)
        
        resp = self.client.get(reverse('resend_activation_email'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('form' in resp.context)
        self.assertEqual(resp.context['form'].__class__, ResendActivationEmailForm)
        
        # Unknown email
        resp = self.client.post(reverse('resend_activation_email'), {'email': self.registration_info['email'] + 'extra'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        
        resp = self.client.post(reverse('resend_activation_email'), {'email': self.registration_info['email']})
        self.assertRedirects(resp, '/', 302, 200)
        self.assertEqual(len(mail.outbox), 2)        
    
    def test_activate(self):
        settings.REGISTRATION_OPEN = True
        os.environ['RECAPTCHA_TESTING'] = 'True'
        # Register a user
        self.client.post(reverse('registration'), self.registration_info)
        
        registration_profile = RegistrationProfile.objects.get(user=User.objects.get(email=self.registration_info['email']))
        
        # Bad activation key
        resp = self.client.get(reverse('registration_activate', args=(registration_profile.activation_key + 'extra',)))
        
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('authentication/activate_unsuccessfull.html' in [temp.name for temp in resp.templates])
        self.failIf(User.objects.get(email=self.registration_info['email']).is_active)
        
        # Correct activation key
        resp = self.client.get(reverse('registration_activate', args=(registration_profile.activation_key,)))
        self.assertRedirects(resp, '/', 302, 200)
        self.assertTrue(User.objects.get(email=self.registration_info['email']).is_active)
