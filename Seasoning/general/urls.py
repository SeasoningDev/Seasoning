"""
Copyright 2012, 2013 Driesen Joep

This file is part of Seasoning.

Seasoning is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Seasoning is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Seasoning.  If not, see <http://www.gnu.org/licenses/>.
    
"""
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
    
    url(r'^contact/form/(.*)/', 'general.views.contact_form'),
    
    # ROBOTS
    (r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    
    # TEST VIEWS
    url(r'^500/$', 'general.views.test_500'),
    
    # Catch all - Check if we have a static page with this url
    url(r'^(.*)/$', 'general.views.static_page')
    
)
