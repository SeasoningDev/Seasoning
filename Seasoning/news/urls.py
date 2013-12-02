from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'news.views.browse_news', name='browse_news'),
    url(r'^(\d*)/$', 'news.views.view_news', name='view_news'),
)
