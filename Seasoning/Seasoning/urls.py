from django.conf.urls import include, url
from django.shortcuts import redirect
import recipes.urls, administration.urls, ingredients.urls
from django.contrib import admin
from administration.admin import seasoning_admin_site
from django.views.generic.base import TemplateView
from administration.views import ContactView

urlpatterns = [
    url(r'^$', lambda r: redirect('browse_recipes')),
    
    url(r'403/', TemplateView.as_view(template_name='403.html')),
    url(r'404/', TemplateView.as_view(template_name='404.html')),
    url(r'500/', TemplateView.as_view(template_name='500.html')),
    
    url(r'contact/$', ContactView.as_view(), name='contact'),
    url(r'terms/$', TemplateView.as_view(template_name='static/terms.html'), name='terms'),
    url(r'thanks/$', TemplateView.as_view(template_name='static/thanks.html'), name='thanks'),
    
    url(r'^ingredients/', include(ingredients.urls)),
    url(r'^recipes/', include(recipes.urls)),
        
    url(r'^admin/', include(administration.urls)),
    url(r'^admin/db/', include(seasoning_admin_site.urls)),
]
