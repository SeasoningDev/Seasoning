from django.contrib import admin
from authentication.models import User, NewEmail, RegistrationProfile
from django.contrib.auth.models import Group

admin.site.register(User)
admin.site.register(RegistrationProfile)
admin.site.register(NewEmail)
admin.site.unregister(Group)