from django.conf.urls import include, url
from django.contrib import admin
from recipes import urls as recipe_urls
from django.shortcuts import redirect

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', lambda r: redirect('browse_recipes')),
    
    url(r'^recipes/', include(recipe_urls)),
]
