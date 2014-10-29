from django.conf.urls import patterns, url
from recipes.views import EditRecipeWizard

urlpatterns = patterns('',
    url(r'^$', 'recipes.views.browse_recipes', name='browse_recipes'),
    url(r'^(\d*)/$', 'recipes.views.view_recipe', name='view_recipe'),
    url(r'^ingredients/(\d*)/(\d*)/$', 'recipes.views.ajax_recipe_ingredients', name='ajax_recipe_ingredients'),
   
    url(r'^ajax/upvote/(\d*)/$', 'recipes.views.upvote', name='upvote_recipe'),
    url(r'^ajax/downvote/(\d*)/$', 'recipes.views.downvote', name='downvote_recipe'),
    
    url(r'^add/$', EditRecipeWizard.as_view(EditRecipeWizard.FORMS), name='add_recipe'),
    url(r'^edit/(?P<recipe_id>\d+)/$', EditRecipeWizard.as_view(EditRecipeWizard.FORMS), name='edit_recipe'),
    url(r'^img/delete/(\d*)/$', 'recipes.views.delete_recipe_image', name='delete_recipe_image'),
    url(r'^delete/(\d*)/$', 'recipes.views.delete_recipe', name='delete_recipe'),
    
    # Statistical data about recipes
    url(r'^data/fpevo/$', 'recipes.views.get_recipe_footprint_evolution'),
    # Unused for now
#     url(r'^data/fprel/$', 'recipes.views.get_relative_footprint'),
    
    url(r'^ingunits/$', 'recipes.views.ajax_ingredient_units'),
    url(r'^markdownpreview/$', 'recipes.views.ajax_markdown_preview'),
    
    url(r'^ajax/$', 'recipes.views.ajax_browse_recipes', name='ajax_browse_recipes'),
    
    url(r'^external/(\d*)/$', 'recipes.views.external_recipe', name='external_recipe'),
)
