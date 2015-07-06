from django.conf.urls import include, url
from django.shortcuts import redirect
import recipes.urls, administration.urls
from django.contrib import admin


urlpatterns = [
    url(r'^$', lambda r: redirect('browse_recipes')),
    
    url(r'^recipes/', include(recipes.urls)),
        
    url(r'^admin/', include(administration.urls)),
    url(r'^admin/db/', include(admin.site.urls)),
]
