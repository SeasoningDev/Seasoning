from django.conf.urls import patterns, include, url
from general.sitemaps import GeneralViewsSitemap, StaticViewSitemap
from ingredients.sitemaps import IngredientViewsSitemap
from recipes.sitemaps import RecipeViewsSitemap

sitemaps = {
    'general': GeneralViewsSitemap,
    'static': StaticViewSitemap,
    'ingredients': IngredientViewsSitemap,
    'recipes': RecipeViewsSitemap,
}

urlpatterns = patterns('',
    
    # Core pages
    (r'^ingredients/', include('ingredients.urls')),
    (r'^recipes/', include('recipes.urls')),
    
    # Registration pages
    (r'^profile/', include('authentication.urls')),
    
     # Comments
    (r'^comments/', include('django.contrib.comments.urls')),
    # FAQ
    (r'^faq/', include('faq.urls')),
    # Logs
    (r'^log/', include('logs.urls')),
    
    # Sitemap
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    
#     (r'^dowser/', include('django_dowser.urls')),
    
    # General Pages
    (r'^', include('general.urls')),
)

import debug_toolbar
urlpatterns += patterns('',
    url(r'^__debug__/', include(debug_toolbar.urls)),
)

from django.conf import settings
# debug stuff to serve static media
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
   )
