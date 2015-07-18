from django.conf.urls import url
from administration import views

urlpatterns = [
    url(r'^$', views.admin_home, name='admin_home'),
    
    url(r'^ajax/recipes/$', views.get_admin_recipes_added_data, name='get_admin_recipes_added_data'),
    
    
    
    url(r'^ingredients/list/$', views.admin_list_ingredients, name='admin_list_ingredients'),
    
    
    
    url(r'^cachupdate/$', views.admin_recipes_update_cached_properties, name='admin_recipes_update_cached_properties'),
    
    
    
    url(r'^scrapers/$', views.admin_scrapers, name='admin_scrapers'),
    url(r'^scrapers/proofread/$', views.admin_proofread_scraped_recipes, name='admin_proofread_scraped_recipes'),
    url(r'^scrapers/proofread/(\d+)/$', views.admin_proofread_scraped_recipe, name='admin_proofread_scraped_recipe'),
    url(r'^scrapers/convert/(\d+)/$', views.admin_convert_scraped_recipe, name='admin_convert_scraped_recipe'),
    
    url(r'^scrapers/scrape/(\d+)/$', views.admin_scrape_recipes, name='admin_scrape_recipes'),
]
