import datetime, re

from authentication.models import User, RegistrationProfile, NewEmail
from django.test import TestCase
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail, management
from django.utils.hashcompat import sha_constructor
from django_dynamic_fixture import G
from recipes.models import Recipe, Cuisine
from django.core.exceptions import PermissionDenied, ValidationError


user_info = {'givenname': 'test',
             'surname': 'user',
             'password': 'haha',
             'email': 'testuser@test.be',
             'date_of_birth': datetime.date.today()}

class UserModelTestCase(TestCase):
    
    def test_rank(self):
        user = G(User)
        self.assertEqual(user.rank(), User.RANKS[0])
        
        G(Cuisine, name='Andere')
        G(Recipe, author=user)
        G(Recipe, author=user)
        self.assertEqual(user.rank(), User.RANKS[1])
    
    def test_recipes_until_next_rank(self):
        user = G(User)
        self.assertEqual(user.recipes_until_next_rank(), 2)
        
        G(Cuisine, name='Andere')
        G(Recipe, author=user)
        G(Recipe, author=user)
        self.assertEqual(user.recipes_until_next_rank(), 2)
    
    def test_clean(self):
        user = G(User)
        user.surname = user.surname + 'extra'
        user.full_clean()
        
        user.name_changed = True
        self.assertRaises(ValidationError, user.full_clean)
        
        user = G(User)
        user.givenname = user.givenname + 'extra'
        user.full_clean()
        
        user.name_changed = True
        self.assertRaises(ValidationError, user.full_clean)
        
    def test_save(self):
        # Make sure the persons name can only be changed once
        user = G(User)
        self.assertEqual(user.name_changed, False)
        new_surname = user.surname + 'extra'
        user.surname = new_surname
        user.save()
        
        self.assertEquals(user.name_changed, True)
        
        user.surname = user.surname + 'extra'
        self.assertRaises(ValidationError, user.save)
    
    def test_delete(self):
        user = G(User)
        G(Cuisine, name='Andere')
        recipe = G(Recipe, author=user)
        
        user.delete()
        self.assertRaises(User.DoesNotExist, lambda: User.objects.get(pk=user.pk))
        self.assertEqual(None, Recipe.objects.get(pk=recipe.pk).author)
        
        user2 = G(User)
        recipe = G(Recipe, author=user2)
        
        user2.delete(delete_recipes=True)
        self.assertRaises(User.DoesNotExist, lambda: User.objects.get(pk=user2.pk))
        self.assertRaises(Recipe.DoesNotExist, lambda: Recipe.objects.get(pk=recipe.pk))
        
class UserManagerTestCase(TestCase):
    
    def test_user_creation(self):
        User.objects.create_user(**user_info)
        new_user = User.objects.get(email="testuser@test.be")
        self.assertEqual(new_user.givenname, 'test')
        self.assertEqual(new_user.surname, 'user')
        self.assertEqual(new_user.date_of_birth, datetime.date.today())
        self.assertEqual(new_user.avatar.url, 'https://www.seasoning.be/media/images/users/no_image.png')
        self.assertEqual(new_user.is_active, False)
        self.assertEqual(new_user.is_staff, False)
        self.assertEqual(new_user.is_superuser, False)
    
    def test_superuser_creation(self):
        User.objects.create_superuser(**user_info)
        new_superuser = User.objects.get(email="testuser@test.be")
        self.assertEqual(new_superuser.is_superuser, True)


class RegistrationManagerTestCase(TestCase):
    
    def test_valid_activation(self):
        """
        Activating a user within the permitted window makes the
        account active, and resets the activation key.
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                                    **user_info)
        profile = RegistrationProfile.objects.get(user=new_user)
        activated = RegistrationProfile.objects.activate_user(profile.activation_key)

        self.failUnless(isinstance(activated, User))
        self.assertEqual(activated.id, new_user.id)
        self.failUnless(activated.is_active)

        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertEqual(profile.activation_key, RegistrationProfile.ACTIVATED)

    def test_expired_activation(self):
        """
        Attempting to activate outside the permitted window does not
        activate the account.
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                                    **user_info)
        new_user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        new_user.save()

        profile = RegistrationProfile.objects.get(user=new_user)
        activated = RegistrationProfile.objects.activate_user(profile.activation_key)

        self.failIf(isinstance(activated, User))
        self.failIf(activated)

        new_user = User.objects.get(email='testuser@test.be')
        self.failIf(new_user.is_active)

        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertNotEqual(profile.activation_key, RegistrationProfile.ACTIVATED)

    def test_activation_invalid_key(self):
        """
        Attempting to activate with a key which is not a SHA1 hash
        fails.
        
        """
        self.failIf(RegistrationProfile.objects.activate_user('foo'))

    def test_activation_already_activated(self):
        """
        Attempting to re-activate an already-activated account fails.
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                                    **user_info)
        profile = RegistrationProfile.objects.get(user=new_user)
        RegistrationProfile.objects.activate_user(profile.activation_key)

        profile = RegistrationProfile.objects.get(user=new_user)
        self.failIf(RegistrationProfile.objects.activate_user(profile.activation_key))

    def test_activation_nonexistent_key(self):
        """
        Attempting to activate with a non-existent key (i.e., one not
        associated with any account) fails.
        
        """
        # Due to the way activation keys are constructed during
        # registration, this will never be a valid key.
        invalid_key = sha_constructor('foo').hexdigest()
        self.failIf(RegistrationProfile.objects.activate_user(invalid_key))   
    
    def test_profile_creation(self):
        """
        Creating a registration profile for a user populates the
        profile with the correct user and a SHA1 hash to use as
        activation key.
        
        """
        new_user = User.objects.create_user(**user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)

        self.assertEqual(RegistrationProfile.objects.count(), 1)
        self.assertEqual(profile.user.id, new_user.id)
        self.failUnless(re.match('^[a-f0-9]{40}$', profile.activation_key))
        self.assertEqual(unicode(profile),
                         "Registration information for test user")

    def test_activation_email(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an
        email.
        
        """
        new_user = User.objects.create_user(**user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [user_info['email']])

    def test_user_creation_with_registration_profile(self):
        """
        Creating a new user populates the correct data, and sets the
        user's account inactive.
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                                    **user_info)
        self.assertEqual(new_user.givenname, 'test')
        self.assertEqual(new_user.surname, 'user')
        self.assertEqual(new_user.email, 'testuser@test.be')
        self.failUnless(new_user.check_password('haha'))
        self.failIf(new_user.is_active)

    def test_user_creation_email(self):
        """
        By default, creating a new user sends an activation email.
        
        """
        RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                         **user_info)
        self.assertEqual(len(mail.outbox), 1)

    def test_user_creation_no_email(self):
        """
        Passing ``send_email=False`` when creating a new user will not
        send an activation email.
        
        """
        RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                         send_email=False,
                                                         **user_info)
        self.assertEqual(len(mail.outbox), 0)
    
    def test_management_command(self):
        """
        The ``cleanupregistration`` management command properly
        deletes expired accounts.
        
        """
        RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                         **user_info)
        expired_user = RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                                        givenname='bob',
                                                                        surname='smith',
                                                                        password='secret',
                                                                        email='bob@example.com',
                                                                        date_of_birth=datetime.date.today())
        expired_user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        expired_user.save()

        management.call_command('cleanupregistration')
        self.assertEqual(RegistrationProfile.objects.count(), 1)
        self.assertRaises(User.DoesNotExist, User.objects.get, email='bob@example.com')
    
class RegistrationProfileModelTestCase(TestCase):

    def test_unexpired_account(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``False``
        within the activation window.
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                                    **user_info)
        profile = RegistrationProfile.objects.get(user=new_user)
        self.failIf(profile.activation_key_expired())

    def test_expired_account(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``True``
        outside the activation window.
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                                    **user_info)
        new_user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        new_user.save()
        profile = RegistrationProfile.objects.get(user=new_user)
        self.failUnless(profile.activation_key_expired())



    def test_expired_user_deletion(self):
        """
        ``RegistrationProfile.objects.delete_expired_users()`` only
        deletes inactive users whose activation window has expired.
        
        """
        RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                         **user_info)
        expired_user = RegistrationProfile.objects.create_inactive_user(site=Site.objects.get_current(),
                                                                        givenname='bob',
                                                                        surname='smith',
                                                                        password='secret',
                                                                        email='bob@example.com',
                                                                        date_of_birth=datetime.date.today())
        expired_user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        expired_user.save()

        RegistrationProfile.objects.delete_expired_users()
        self.assertEqual(RegistrationProfile.objects.count(), 1)
        self.assertRaises(User.DoesNotExist, User.objects.get, email='bob@example.com')    

class NewEmailModelTestCase(TestCase):
    
    def test_send_newemail_email(self):
        new_email = G(NewEmail)
        
        new_email.send_new_email_email(Site.objects.get_current())
        
        # One for registration, one for new email
        self.assertEqual(len(mail.outbox), 1)

class NewEmailManagerTestCase(TestCase):
    
    def test_create_inactive_email(self):
        user = G(User)
        old_email = user.email
        
        new_email = NewEmail.objects.create_inactive_email(user, user.email + 'extra', Site.objects.get_current(), False)
        
        self.assertEqual(new_email.user, user)
        self.assertEqual(new_email.email, user.email + 'extra')
        self.assertEqual(user.email, old_email)
        self.assertEqual(len(mail.outbox), 0)
        
        new_email = NewEmail.objects.create_inactive_email(user, user.email + 'extra2', Site.objects.get_current())
        
        # Previous email should be deleted
        self.assertEqual(len(NewEmail.objects.all()), 1)
        self.assertEqual(len(mail.outbox), 1)
    
    def test_activate_email(self):
        user = G(User)
        old_email = user.email
        
        new_email = NewEmail.objects.create_inactive_email(user, user.email + 'extra', Site.objects.get_current(), False)
        returned_user = NewEmail.objects.activate_email(user, new_email.activation_key)
        
        user = User.objects.get(pk=user.pk)
        self.assertEqual(user.email, returned_user.email)
        self.assertEqual(user.email, old_email + 'extra')
        self.assertEqual(len(NewEmail.objects.all()), 0)
        
        self.assertFalse(NewEmail.objects.activate_email(user, 'wrong'))
        self.assertFalse(NewEmail.objects.activate_email(user, new_email.activation_key))
    