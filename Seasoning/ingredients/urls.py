from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # Ingredient Pages
    url(r'^$', 'ingredients.views.browse_ingredients', name='browse_ingredients'),
    url(r'^(\d*)/$', 'ingredients.views.view_ingredient', name='view_ingredient'),
    
    # AJAX Calls
    url(r'^ajax/names/$', 'ingredients.views.ajax_ingredient_name_list', name='ajax_ingredient_name_list'),
    url(r'^ajax/list/$', 'ingredients.views.ajax_ingredient_list', name='ajax_ingredient_list'),
    url(r'^ajax/avail/$', 'ingredients.views.ajax_ingredient_availability', name='ajax_ingredient_availability'),
)
