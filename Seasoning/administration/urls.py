from django.conf.urls import url
from administration import views
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='admin/admin_base.html'), name='admin_home'),
    
    url(r'^scrapers/$', views.admin_scrapers, name='admin_scrapers')
]
