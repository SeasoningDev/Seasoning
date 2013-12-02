"""
Copyright 2012, 2013 Driesen Joep

This file is part of Seasoning.

Seasoning is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Seasoning is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Seasoning.  If not, see <http://www.gnu.org/licenses/>.
    
"""
from django.conf.urls import patterns, include
from general.sitemaps import GeneralViewsSitemap, StaticViewSitemap
from ingredients.sitemaps import IngredientViewsSitemap
from news.sitemaps import NewsViewsSitemap
from recipes.sitemaps import RecipeViewsSitemap

sitemaps = {
    'general': GeneralViewsSitemap,
    'static': StaticViewSitemap,
    'news': NewsViewsSitemap,
    'ingredients': IngredientViewsSitemap,
    'recipes': RecipeViewsSitemap,
}

urlpatterns = patterns('',
    # Core pages
    (r'^ingredients/', include('ingredients.urls')),
    (r'^recipes/', include('recipes.urls')),
    
    # Registration pages
    (r'^', include('authentication.urls')),
    
     # Comments
    (r'^comments/', include('django.contrib.comments.urls')),
    # FAQ
    (r'^faq/', include('faq.urls')),
    # News
    (r'^news/', include('news.urls')),
    
    # Sitemap
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    
    # General Pages
    (r'^', include('general.urls')),
)

from django.conf import settings
# debug stuff to serve static media
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
   )
