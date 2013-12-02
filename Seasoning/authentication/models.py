import datetime, hashlib, random, re, time

from django.db import models, transaction
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password, is_password_usable
from django.contrib.auth.models import BaseUserManager
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from imagekit.models.fields import ProcessedImageField
from imagekit.processors.resize import ResizeToFill


def get_image_filename(instance, old_filename):
    """
    Get a new filename for a user image
    
    """
    filename = str(time.time()) + '.png'
    return 'images/users/' + filename


class UserManager(BaseUserManager):
    
    def create_user(self, givenname, surname, email, date_of_birth, password=None):
        """
        Creates and saves a User with the given name, email, date of
        birth and password.
        
        """
        user = self.model(givenname=givenname,
                          surname=surname,
                          email=UserManager.normalize_email(email),
                          date_of_birth=date_of_birth)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, givenname, surname, email, date_of_birth, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        
        """
        user = self.create_user(givenname=givenname,
                                surname=surname,
                                email=UserManager.normalize_email(email),
                                date_of_birth=date_of_birth,
                                password=password)
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(models.Model):
    
    class Meta:
        db_table = 'user'
    
    RANKS = {0: 'Groentje', 1: 'Keukenhulp', 2: 'Leerjongen',
             3: 'Hobbykok', 4: 'Fijnproever', 5: 'Sous Chef',
             6: 'Chef Kok', 7: 'Meesterkok', 8: 'Saturnus'}
    
    objects = UserManager()
    
    email = models.EmailField(
        verbose_name=_(_('email address')),
        max_length=255,
        unique=True,
        db_index=True,
    )
    
    givenname = models.CharField(_('given name'), max_length=30,
                                help_text=_('30 characters or fewer, only letters allowed. '
                                            'Your name will be used to identify you on Seasoning.'),
                                validators=[validators.RegexValidator(re.compile('[a-zA-Z -]{2,}'), _('Enter a valid Given Name.'), 'invalid')])
    
    surname = models.CharField(_('surname'), max_length=50,
                                help_text=_('50 characters or fewer, only letters allowed '
                                            'Your name will be used to identify you on Seasoning.'),
                                validators=[validators.RegexValidator(re.compile('[a-zA-Z -]{2,}'), _('Enter a valid Surname.'), 'invalid')])
    
    # Field to check if user has changed his name (name can only be changed once to avoid abuse)
    name_changed = models.BooleanField(default=False, editable=False)
    
    password = models.CharField(_('password'), max_length=128, null=True)
    
    avatar = ProcessedImageField([ResizeToFill(250, 250)], format='PNG', \
                                  upload_to=get_image_filename, default='images/users/no_image.png')
    
    date_of_birth = models.DateField()
        
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(_(_('date joined')), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), default=timezone.now)

    facebook_id = models.CharField(max_length=30, editable=False, null=True)
    twitter_id = models.CharField(max_length=30, editable=False, null=True)
    google_id = models.CharField(max_length=30, editable=False, null=True)
    openid_id = models.CharField(max_length=30, editable=False, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['givenname', 'surname', 'password', 'date_of_birth']
    
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        
        # Theses should only be set by the save method! Used for checking
        # if a users has changed his name.
        self.__cached_givenname__ = self.givenname
        self.__cached_surname__ = self.surname

    def get_full_name(self):
        return ' '.join((self.givenname, self.surname))

    def get_short_name(self):
        return self.givenname
    
    def get_username(self):
        return self.email
    
    def rank(self):
        # Get the log2(recipes_added_by_user) rounded down. This is the current
        # rank of the user. Minimum rank is 0, maximum rank is 8
        # x.bit_length() - 1 = log2(x) (except for x=0 -> x.bit_length() = 0)
        rank_num = min(8, max(0, len(self.recipes.all()).bit_length() - 1))
        return self.RANKS[rank_num]
    
    def recipes_until_next_rank(self):
        ao_recipes = len(self.recipes.all())
        current_rank = min(8, max(0, ao_recipes.bit_length() - 1))
        next_rank = current_rank + 1
        if next_rank >= 8:
            return 0
        return 2**next_rank - ao_recipes

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        
        """
        send_mail(subject, message, from_email, [self.email])

    def __unicode__(self):
        return self.get_full_name()

    def natural_key(self):
        return (self.email,)

    def is_anonymous(self):
        """
        Always returns False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Sets a value that will never be a valid hash
        self.password = make_password(None)

    def has_usable_password(self):
        return is_password_usable(self.password)
    
    def clean(self):
        """
        Checks if the user has changed his name. If so, this is only allowed if the user has
        not changed his name before.
        If the users' previous name was nothing, no change is counted. This can only occur before
        the first save.
        
        """
        if self.name_changed:
            # This user has already changed his or her name
            if not (self.__cached_givenname__ == '' and self.__cached_surname__ == ''):
                # Check if the name of the user was changed
                if self.givenname != self.__cached_givenname__ or self.surname != self.__cached_surname__:
                    raise ValidationError('Name can only be changed once!')
        
    def save(self, *args, **kwargs):
        """
        Checks if the user has changed his name. If so, this is only allowed if the user has
        not changed his name before.
        If the users' previous name was nothing, no change is counted. This can only occur before
        the first save.
        
        """
        self.full_clean()
        if self.givenname != self.__cached_givenname__ or self.surname != self.__cached_surname__:
            if not (self.__cached_givenname__ == '' and self.__cached_surname__ == ''):
                self.name_changed = True
        super(User, self).save(*args, **kwargs);
        self.__cached_givenname__ = self.givenname
        self.__cached_surname__ = self.surname
    
    def delete(self, delete_recipes=False, *args, **kwargs):
        """
        Delete this user and the recipes added by this user 
        if this is wanted
        
        """
        if not delete_recipes:
            self.recipes.all().update(author=None)
        super(User, self).delete(*args, **kwargs)
        

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return False

    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return False

try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now


SHA1_RE = re.compile('^[a-f0-9]{40}$')


class RegistrationManager(models.Manager):
    """
    Custom manager for the ``RegistrationProfile`` model.
    
    The methods defined here provide shortcuts for account creation
    and activation (including generation and emailing of activation
    keys), and for cleaning out expired inactive accounts.
    
    """
    def activate_user(self, activation_key):
        """
        Validate an activation key and activate the corresponding
        ``User`` if valid.
        
        If the key is valid and has not expired, return the ``User``
        after activating.
        
        If the key is not valid or has expired, return ``False``.
        
        If the key is valid but the ``User`` is already active,
        return ``False``.
        
        To prevent reactivation of an account which has been
        deactivated by site administrators, the activation key is
        reset to the string constant ``RegistrationProfile.ACTIVATED``
        after successful activation.

        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                return user
        return False
    
    def create_inactive_user(self, givenname, surname, email, password, date_of_birth,
                             site, send_email=True):
        """
        Create a new, inactive ``User``, generate a
        ``RegistrationProfile`` and email its activation key to the
        ``User``, returning the new ``User``.

        By default, an activation email will be sent to the new
        user. To disable this, pass ``send_email=False``.
        
        """
        new_user = User.objects.create_user(givenname, surname, email, date_of_birth, password=password)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email(site)

        return new_user
    create_inactive_user = transaction.commit_on_success(create_inactive_user)

    def create_profile(self, user):
        """
        Create a ``RegistrationProfile`` for a given
        ``User``, and return the ``RegistrationProfile``.
        
        The activation key for the ``RegistrationProfile`` will be a
        SHA1 hash, generated from a combination of the ``User``'s
        email and a random salt.
        
        """
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        email = user.email
        if isinstance(email, unicode):
            email = email.encode('utf-8')
        activation_key = hashlib.sha1(salt+email).hexdigest()
        return self.create(user=user,
                           activation_key=activation_key)
        
    def delete_expired_users(self):
        """
        Remove expired instances of ``RegistrationProfile`` and their
        associated ``User``s.
        
        Accounts to be deleted are identified by searching for
        instances of ``RegistrationProfile`` with expired activation
        keys, and then checking to see if their associated ``User``
        instances have the field ``is_active`` set to ``False``; any
        ``User`` who is both inactive and has an expired activation
        key will be deleted.
        
        It is recommended that this method be executed regularly as
        part of your routine site maintenance; this application
        provides a custom management command which will call this
        method, accessible as ``manage.py cleanupregistration``.
        
        Regularly clearing out accounts which have never been
        activated serves two useful purposes:
        
        1. It alleviates the ocasional need to reset a
           ``RegistrationProfile`` and/or re-send an activation email
           when a user does not receive or does not act upon the
           initial activation email; since the account will be
           deleted, the user will be able to simply re-register and
           receive a new activation key.
        
        2. It prevents the possibility of a malicious user registering
           one or more accounts and never activating them (thus
           denying the use of those emails to anyone else); since
           those accounts will be deleted, the emails will become
           available for use again.
        
        If you have a troublesome ``User`` and wish to disable their
        account while keeping it in the database, simply delete the
        associated ``RegistrationProfile``; an inactive ``User`` which
        does not have an associated ``RegistrationProfile`` will not
        be deleted.
        
        """
        for profile in self.all():
            try:
                if profile.activation_key_expired():
                    user = profile.user
                    if not user.is_active:
                        user.delete()
                        profile.delete()
            except User.DoesNotExist:
                profile.delete()

class RegistrationProfile(models.Model):
    """
    A simple profile which stores an activation key for use during
    user account registration.
    
    Generally, you will not want to interact directly with instances
    of this model; the provided manager includes methods
    for creating and activating new accounts, as well as for cleaning
    out accounts which have never been activated.
    
    While it is possible to use this model as the value of the
    ``AUTH_PROFILE_MODULE`` setting, it's not recommended that you do
    so. This model's sole purpose is to store data temporarily during
    account registration and activation.
    
    """
    ACTIVATED = u"ALREADY_ACTIVATED"
    
    user = models.OneToOneField(User)
    activation_key = models.CharField(_('activation key'), max_length=40)
    
    objects = RegistrationManager()
    
    class Meta:
        db_table = 'registrationprofile'
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')
    
    def __unicode__(self):
        return u"Registration information for %s" % self.user
    
    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.
        
        Key expiration is determined by a two-step process:
        
        1. If the user has already activated, the key will have been
           reset to the string constant ``ACTIVATED``. Re-activating
           is not permitted, and so this method returns ``True`` in
           this case.

        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.
        
        """
        expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.activation_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= datetime_now())
    activation_key_expired.boolean = True

    def send_activation_email(self, site):
        """
        Send an activation email to the user associated with this
        ``RegistrationProfile``.
        
        The activation email will make use of two templates:

        ``authentication/activation_email_subject.txt``
            This template will be used for the subject line of the
            email. Because it is used as the subject line of an email,
            this template's output **must** be only a single line of
            text; output longer than one line will be forcibly joined
            into only a single line.

        ``authentication/activation_email.txt``
            This template will be used for the body of the email.

        These templates will each receive the following context
        variables:

        ``activation_key``
            The activation key for the new account.

        ``expiration_days``
            The number of days remaining during which the account may
            be activated.

        ``site``
            An object representing the site on which the user
            registered; depending on whether ``django.contrib.sites``
            is installed, this may be an instance of either
            ``django.contrib.sites.models.Site`` (if the sites
            application is installed) or
            ``django.contrib.sites.models.RequestSite`` (if
            not). Consult the documentation for the Django sites
            framework for details regarding these objects' interfaces.

        """
        ctx_dict = {'activation_key': self.activation_key,
                    'site': site}
        subject = render_to_string('authentication/activation_email_subject.txt',
                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        message_text = render_to_string('authentication/activation_email.txt',
                                        ctx_dict)
        message_html = render_to_string('authentication/activation_email.html',
                                        ctx_dict)

        msg = EmailMultiAlternatives(subject, message_text, settings.DEFAULT_FROM_EMAIL, [self.user.email])
        msg.attach_alternative(message_html, "text/html")
        msg.send()

class NewEmailManager(models.Manager):
    """
    Custom manager for the ``NewEmail`` model
    
    """
    def create_inactive_email(self, user, new_email, site, send_email=True):
        """
        Create a new, inactive email for a given user, generate a
        ``NewEmail`` and email its activation key to the
        ``User``, returning the new ``NewEmail`` object.

        By default, an activation email will be sent to the new
        user. To disable this, pass ``send_email=False``.
        
        If the user already had a ``NewEmail`` waiting to be activated, this
        object will be replaced by the new ``NewEmail``.
        
        """
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        try:
            old_new_email = self.get(user=user)
            old_new_email.delete()
        except self.model.DoesNotExist:
            pass
        email = user.email
        if isinstance(email, unicode):
            email = email.encode('utf-8')
        activation_key = hashlib.sha1(salt+email).hexdigest()
        inactive_email = self.create(user=user,
                                     activation_key=activation_key,
                                     email=new_email)
        
        if send_email:
            inactive_email.send_new_email_email(site)

        return inactive_email
    
    def activate_email(self, user, activation_key):
        """
        Validate an activation key corresponding to a given user
        
        If the key is valid, return the new email addres after activating, and
        delete the ``NewEmail`` object in the database and return the updated
        ``User`` object.
        
        If the key is not valid, return ``False``.
        
        """
        if SHA1_RE.search(activation_key):
            try:
                new_email = self.get(user=user, activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            user = new_email.user
            user.email = new_email.email
            user.save()
            new_email.delete()
            return user
        return False

class NewEmail(models.Model):
    """
    This model stores a new email of an account while it has not been activated
    
    """
    class Meta:
        db_table = 'newemail'
    
    user = models.ForeignKey(User, primary_key=True, related_name='new_emails')
    activation_key = models.CharField(_('activation key'), unique=True, max_length=40)
    email = models.EmailField(
        max_length=255,
        unique=True
    )
    
    objects = NewEmailManager()
    
    def send_new_email_email(self, site):
        """
        Send an email containing an activation link to this objects email.
        
        """
        ctx_dict = {'activation_key': self.activation_key,
                    'site': site,
                    'user': self.user}
        subject = render_to_string('authentication/change_email_email_subject.txt',
                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        
        message_text = render_to_string('authentication/change_email_email.txt',
                                        ctx_dict)
        message_html = render_to_string('authentication/change_email_email.html',
                                        ctx_dict)

        msg = EmailMultiAlternatives(subject, message_text, settings.DEFAULT_FROM_EMAIL, [self.email])
        msg.attach_alternative(message_html, "text/html")
        msg.send()
    
    def __unicode__(self):
        return self.email

