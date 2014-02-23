from django.contrib import admin
from django.contrib.auth.models import Group
from authentication.models import User, NewEmail, RegistrationProfile

class UserAdmin(admin.ModelAdmin):
    model = User
    readonly_fields = ('facebook_id', 'google_id')
    
    
admin.site.register(User, UserAdmin)
admin.site.register(RegistrationProfile)
admin.site.register(NewEmail)
admin.site.unregister(Group)