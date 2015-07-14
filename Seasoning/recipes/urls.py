from django.conf.urls import url
from recipes import views

urlpatterns = [
    url(r'^$', views.browse_recipes, name='browse_recipes'),
    url(r'^(\d+)/$', views.view_recipe, name='view_recipe'),
    
    url(r'^get/$', views.get_recipes, name='get_recipes'),
    url(r'^get/(\d+)/', views.get_recipes, name='get_recipes_max'),
]
