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
from recipes.views import delete_recipe_comment
from recipes.views import EditRecipeWizard

urlpatterns = patterns('',
    url(r'^$', 'recipes.views.browse_recipes', name='browse_recipes'),
    url(r'^(\d*)/$', 'recipes.views.view_recipe', name='view_recipe'),
   
    url(r'^portions/$', 'recipes.views.get_recipe_portions'),
    url(r'^vote/$', 'recipes.views.vote'),
    url(r'^removevote/(\d*)/$', 'recipes.views.remove_vote'),
    url(r'^deletecomment/(\d*)/(\d*)/$', delete_recipe_comment),
    
    url(r'^add/$', EditRecipeWizard.as_view(EditRecipeWizard.FORMS)),
    url(r'^edit/(?P<recipe_id>\d+)/$', EditRecipeWizard.as_view(EditRecipeWizard.FORMS)),
    url(r'^delete/(\d*)/$', 'recipes.views.delete_recipe'),
    
    # Statistical data about recipes
    url(r'^data/fpevo/$', 'recipes.views.get_recipe_footprint_evolution'),
    url(r'^data/fprel/$', 'recipes.views.get_relative_footprint'),
    
    url(r'^ingunits/$', 'recipes.views.ajax_ingredient_units'),
    url(r'^markdownpreview/$', 'recipes.views.ajax_markdown_preview'),
)
