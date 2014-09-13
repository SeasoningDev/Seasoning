from django.conf.urls import patterns, url
from recipes.views import delete_recipe_comment, EditRecipeWizard

urlpatterns = patterns('',
    url(r'^$', 'recipes.views.browse_recipes', name='browse_recipes'),
    url(r'^(\d*)/$', 'recipes.views.view_recipe', name='view_recipe'),
   
    url(r'^portions/$', 'recipes.views.get_recipe_portions'),
    url(r'^vote/$', 'recipes.views.vote'),
    url(r'^removevote/(\d*)/$', 'recipes.views.remove_vote'),
    url(r'^deletecomment/(\d*)/(\d*)/$', delete_recipe_comment, name='delete_comment'),
    
    url(r'^add/$', EditRecipeWizard.as_view(EditRecipeWizard.FORMS), name='add_recipe'),
    url(r'^edit/(?P<recipe_id>\d+)/$', EditRecipeWizard.as_view(EditRecipeWizard.FORMS), name='edit_recipe'),
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
