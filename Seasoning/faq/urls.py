from django.conf.urls import patterns, url
from faq.views import topic_list

urlpatterns = patterns('',
    url(r'^$', topic_list, name = 'faq'),
)