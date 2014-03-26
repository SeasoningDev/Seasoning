from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views.generic.base import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    # Home Page
    url(r'^$', 'general.views.home', name='home'),
    
    # Admin
    url(r'^admin/ingredients/list/$', 'ingredients.views.list_ingredients', name='list_ingredients'),
    (r'^admin/', include(admin.site.urls)),
    
    # Backup Database
    url(r'^backup/$', 'general.views.backup_db'),
    url(r'^upload/img/$', 'general.views.upload_static_image'),
    
    url(r'^contribute/$', 'general.views.contribute', name='contribute'),
    url(r'^donate/$', 'general.views.donate', name='donate'),
    url(r'^donate/success/$', 'general.views.donate_success'),
    
    url(r'^contact/form/(.*)/', 'general.views.contact_form', name='contact'),
    
    # ROBOTS
    (r'^robots\.txt$', TemplateView.as_view(template_name='misc/robots.txt', content_type='text/plain')),
    
    # TEST VIEWS
    url(r'^500/$', 'general.views.test_500'),
    
    # Google verification file
    url(r'^google99ea56259237cc2a.html/$', TemplateView.as_view(template_name='misc/google99ea56259237cc2a.html', content_type='text/plain')),
    
    # Catch all - Check if we have a static page with this url
    url(r'^(.*)/$', 'general.views.static_page', name='static_page')
    
)
