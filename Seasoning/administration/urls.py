from django.conf.urls import url
from administration import views

urlpatterns = [
    url(r'^$', views.admin_home, name='admin_home'),
    
    url(r'^ajax/recipes/$', views.get_admin_recipes_added_data, name='get_admin_recipes_added_data'),
    
    
    
    url(r'^ingredients/list/$', views.admin_list_ingredients, name='admin_list_ingredients'),
    
    
    
    url(r'^cacheupdate/$', views.admin_recipes_update_cached_properties, name='admin_recipes_update_cached_properties'),
    url(r'^cacheupdate/(\d+)/$', views.admin_recipes_update_cached_properties, name='admin_recipes_update_cached_properties_single'),
    
    
    
    url(r'^scrapers/$', views.admin_scrapers, name='admin_scrapers'),
    url(r'^scrapers/proofread/$', views.admin_proofread_scraped_recipes, name='admin_proofread_scraped_recipes'),
    url(r'^scrapers/proofread/(\d+)/$', views.admin_proofread_scraped_recipe, name='admin_proofread_scraped_recipe'),
    url(r'^scrapers/convert/(\d+)/$', views.admin_convert_scraped_recipe, name='admin_convert_scraped_recipe'),
    
    url(r'^scrapers/scrape/(\d+)/$', views.admin_scrape_recipes, name='admin_scrape_recipes'),
    
    
    url(r'^analytics/$', views.admin_analytics, name='admin_analytics'),
    url(r'^analytics/2/$', views.admin_analytics2, name='admin_analytics2'),
    url(r'^analytics/parse/uwsgi/$', views.admin_analytics_parse_uwgsi_log, name='admin_analytics_parse_uwgsi_log'),
    
    url(r'^ajax/history/uwsgi/(\d+)/(\d+)/$', views.get_request_history, name='get_request_history'),
    url(r'^ajax/ips/uwsgi/(\d+)/(\d+)/$', views.get_distinct_ips, name='get_distinct_ips'),
    
    
    
    url(r'^download/db/', views.admin_download_db_backup, name='admin_download_db_backup'),
    url(r'^download/media/', views.admin_download_media_backup, name='admin_download_media_backup'),
]
