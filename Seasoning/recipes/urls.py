from django.conf.urls import url
from recipes import views

urlpatterns = [
    url(r'^$', views.browse_recipes, name='browse_recipes'),
    url(r'^(\d+)/$', views.view_recipe, name='view_recipe'),
    url(r'^analyze/(\d+)/$', views.view_recipe_footprint_analysis, name='view_recipe_footprint_analysis'),
    
    url(r'^get/$', views.get_recipes, name='get_recipes'),
    url(r'^get/(\d+)/$', views.get_recipes, name='get_recipes_max'),
    url(r'^get/analyze/breakdown/(\d+)/$', views.get_recipe_footprint_breakdown_data, name='get_recipe_footprint_breakdown_data'),
    url(r'^get/analyze/relative/(\d+)/$', views.get_recipe_relative_footprint_data, name='get_recipe_relative_footprint_data'),
]
