from django.conf.urls import include, url
from django.contrib import admin
from recipes import urls as recipe_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^recipes/', include(recipe_urls)),
]
