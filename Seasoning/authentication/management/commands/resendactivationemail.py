"""
A management command which lets you send activation emails
to registered users who have not received theirs for whatever
reason.

"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from authentication.models import RegistrationProfile


class Command(BaseCommand):
    args = '<user_id user_id ...>'
    help = "Resend an activation email to the given user"

    def handle(self, *args, **options):
        for user_id in args:
            try:
                registrationprofile = RegistrationProfile.objects.get(user__id=user_id)
            except RegistrationProfile.DoesNotExist:
                raise CommandError('User "%s" does not have registration profile' % user_id)
            if registrationprofile.user.is_active:
                raise CommandError('User "%s" is already active' % user_id)
            registrationprofile.send_activation_email(Site.objects.get_current())
