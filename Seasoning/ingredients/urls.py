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
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # Ingredient Pages
    url(r'^$', 'ingredients.views.view_ingredients', name='view_ingredients'),
    url(r'^(\d*)/$', 'ingredients.views.view_ingredient', name='view_ingredient'),
    
    # AJAX Calls
    url(r'^ing_list/$', 'ingredients.views.ajax_ingredient_name_list'),
    url(r'^ing_avail/$', 'ingredients.views.ajax_ingredient_availability'),
)
