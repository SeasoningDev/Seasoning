from django.conf.urls import patterns, url
from authentication.backends import RegistrationBackend

urlpatterns = patterns('',
    
    # Registration urls                   
    url(r'^register/$', 'authentication.views.register', {'backend': RegistrationBackend},
        name='registration'),
    url(r'^register/closed/$', 'authentication.views.registration_closed',
        name='registration_disallowed'),
    url(r'^register/complete/$', 'authentication.views.registration_complete',
        name='registration_complete'),
    
    # Activation urls
    url(r'^activate/resend/$', 'authentication.views.resend_activation_email',
        name='resend_activation_email'),
    url(r'^activate/(?P<activation_key>\w+)/$', 'authentication.views.activate', {'backend': RegistrationBackend},
        name='registration_activate'),
    
    # Login urls
    url(r'^login/$', 'authentication.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'authentication/logout.html'},
        name='logout'),
    url(r'^password/reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^password/reset/done/$', 'django.contrib.auth.views.password_reset_done', 
        {'template_name':'authentication/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name':'authentication/password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^password/reset/complete/$', 'django.contrib.auth.views.password_reset_complete', 
        {'template_name':'authentication/password_reset_complete.html'},
        name='password_reset_complete'),
    
    # Profile urls
    url(r'^$', 'authentication.views.account_settings', name='my_profile'),
    url(r'^(\d.*)/$', 'authentication.views.account_settings', name='user_profile'),
    url(r'^settings/$', 'authentication.views.account_settings_profile'),
    url(r'^settings/social/$', 'authentication.views.account_settings_social'),
    url(r'^settings/privacy/$', 'authentication.views.account_settings_privacy'),
    url(r'^delete/$', 'authentication.views.account_delete'),
    url(r'^password/change/$', 'authentication.views.change_password',
        name='password_change'),
    url(r'^email/change/(?P<activation_key>\w+)/$', 'authentication.views.change_email'),
    
    # Social logins
    url(r'^auth/(.*)/register/', 'authentication.views.social_register'),
    url(r'^auth/(.*)/connect/', 'authentication.views.social_connect'),
    url(r'^auth/(.*)/disconnect/', 'authentication.views.social_disconnect'),
    url(r'^auth/(.*)/$', 'authentication.views.social_auth'),
)
