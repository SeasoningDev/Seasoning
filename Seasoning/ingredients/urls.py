from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # Ingredient Pages
    url(r'^$', 'ingredients.views.view_ingredients', name='view_ingredients'),
    url(r'^(\d*)/$', 'ingredients.views.view_ingredient', name='view_ingredient'),
    
    # AJAX Calls
    url(r'^ing_list/$', 'ingredients.views.ajax_ingredient_name_list'),
    url(r'^ajax/$', 'ingredients.views.ajax_ingredient_list', name='ajax_ingredient_list'),
    url(r'^ing_avail/$', 'ingredients.views.ajax_ingredient_availability'),
)
