from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'logs.views.view_logs', name='view_logs'),
    url(r'^parse/$', 'logs.views.parse_logs', name='parse_logs'),
    
    url(r'^ajax/swh/', 'logs.views.ajax_site_wide_history', name='ajax_site_wide_history')
)
