from django.test import TestCase
from authentication.models import User, RegistrationProfile
import authentication.forms
import datetime
import os
from authentication.backends import RegistrationBackend
from django.contrib.sites.models import Site
from django import forms
from django_dynamic_fixture import G

class RegistrationFormTestCase(TestCase):
    
    def test_validation(self):        
        form = authentication.forms.RegistrationForm(data={'givenname': 'test',
                                                           'surname': 'user',
                                                           'password': 'haha',
                                                           'password2': 'haha2',
                                                           'email': 'testuser@test.be',
                                                           'date_of_birth': datetime.date.today(),
                                                           'tos': False,
                                                           'captcha': ''})
        self.assertEqual(len(form.errors), 3)
        self.assertTrue('captcha' in form.errors)
        self.assertTrue('__all__' in form.errors)
        self.assertTrue('tos' in form.errors)

class SocialRegistrationFormTestCase(TestCase):
    
    def test_validation(self):
        form = authentication.forms.SocialRegistrationForm(data={'tos': True})
        self.assertTrue(form.is_valid())
        form = authentication.forms.SocialRegistrationForm(data={'tos': True,
                                                                 'password': '1'})
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('__all__' in form.errors)
        form = authentication.forms.SocialRegistrationForm(data={'tos': True,
                                                                 'password': '1',
                                                                 'password2': '2'})
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('__all__' in form.errors)
        form = authentication.forms.SocialRegistrationForm(data={'tos': True,
                                                                 'password': '1',
                                                                 'password2': '1'})
        self.assertTrue(form.is_valid())

class ResendActivationEmailFormTestCase(TestCase):
    
    def test_validation(self):
        form = authentication.forms.ResendActivationEmailForm(data={'email': 'test@test.com'})
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('email' in form.errors)
        
        profile = G(RegistrationProfile)
        form = authentication.forms.ResendActivationEmailForm(data={'email': profile.user.email})
        self.assertTrue(form.is_valid())
        
        profile.user.is_active = True
        profile.user.save()
        form = authentication.forms.ResendActivationEmailForm(data={'email': profile.user.email})
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('email' in form.errors)
        
        profile.activation_key = RegistrationProfile.ACTIVATED
        profile.save()
        profile.user.is_active = False
        profile.user.save()
        form = authentication.forms.ResendActivationEmailForm(data={'email': profile.user.email})
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('email' in form.errors)
        
class AccountSettingsFormTestCase(TestCase):
    
    def test_name_fields(self):
        user = G(User)
        user.name_changed = True
        
        form = authentication.forms.AccountSettingsForm(instance=user,
                                                        data={'email': user.email})
        self.assertFalse('givenname' in form.fields)
        self.assertFalse('surname' in form.fields)
        
    def test_validation(self):
        user = G(User)
        
        form = authentication.forms.AccountSettingsForm(instance=user,
                                                        data={'givenname': user.givenname,
                                                              'surname': user.surname,
                                                              'email': user.email})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.new_email, None)
        
        form = authentication.forms.AccountSettingsForm(instance=user,
                                                        data={'givenname': user.givenname,
                                                              'surname': user.surname,
                                                              'email': user.email + 'extra'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.new_email, user.email + 'extra')
        form.cleaned_data['email'] = user.email
    
class DeleteAccountFormTestCase(TestCase):
    
    def test_validation(self):
        form = authentication.forms.DeleteAccountForm(data={'checkstring': 'Wrong',
                                                            'delete_recipes': True})
        self.assertEqual(len(form.errors), 1)
        self.assertTrue('checkstring' in form.errors)
        
        form = authentication.forms.DeleteAccountForm(data={'checkstring': 'DELETEME',
                                                            'delete_recipes': True})
        self.assertTrue(form.is_valid())
        
        form = authentication.forms.DeleteAccountForm(data={'checkstring': 'DELETEME'})
        self.assertTrue(form.is_valid())
