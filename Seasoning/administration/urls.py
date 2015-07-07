from django.conf.urls import url
from administration import views
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='admin/admin_base.html'), name='admin_home'),
    
    url(r'^scrapers/$', views.admin_scrapers, name='admin_scrapers'),
    url(r'^scrapers/proofread/$', views.admin_proofread_scraped_recipes, name='admin_proofread_scraped_recipes'),
    url(r'^scrapers/proofread/(\d+)/$', views.admin_proofread_scraped_recipe, name='admin_proofread_scraped_recipe'),
    
    url(r'^scrapers/scrape/eva/$', views.admin_scrape_eva, name='admin_scrape_eva'),
]
