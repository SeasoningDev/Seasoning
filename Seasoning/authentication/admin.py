from django.contrib import admin
from django.contrib.auth.models import Group
from authentication.models import User, NewEmail, RegistrationProfile

admin.site.register(User)
admin.site.register(RegistrationProfile)
admin.site.register(NewEmail)
admin.site.unregister(Group)