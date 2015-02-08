from django.conf.urls import patterns, url

urlpatterns = patterns('',
    # BROWSE RECIPES
    url(r'^$', 'recipes.views.browse_recipes', name='browse_recipes'),
    url(r'^ajax/$', 'recipes.views.ajax_browse_recipes', name='ajax_browse_recipes'),
    
    # VIEW RECIPE
    url(r'^(\d*)/$', 'recipes.views.view_recipe', name='view_recipe'),
    url(r'^i/(\d*)/$', 'recipes.views.view_recipe', kwargs={'incomplete': True},
        name='view_incomplete_recipe'),
    
    url(r'^img/delete/(\d*)/$', 'recipes.views.delete_recipe_image', name='delete_recipe_image'),
    
    url(r'^ajax/upvote/(\d*)/$', 'recipes.views.upvote', name='upvote_recipe'),
    url(r'^ajax/downvote/(\d*)/$', 'recipes.views.downvote', name='downvote_recipe'),
    
    url(r'^ingredients/(\d*)/(\d*)/$', 'recipes.views.ajax_recipe_ingredients', 
        name='ajax_recipe_ingredients'),
    url(r'^ingredients/i/(\d*)/(\d*)/$', 'recipes.views.ajax_recipe_ingredients', 
        kwargs={'incomplete': True}, name='ajax_incomplete_recipe_ingredients'),
    
    url(r'^external/(\d*)/$', 'recipes.views.external_recipe', name='external_recipe'),
   
    
    # EDIT RECIPE
    url(r'^add/$', 'recipes.views.add_recipe', name='add_recipe'),
    url(r'^edit/(\d*)/$', 'recipes.views.edit_recipe', name='edit_recipe'),
    url(r'^edit/i/(\d*)/$', 'recipes.views.edit_recipe', kwargs={'incomplete': True},
        name='edit_incomplete_recipe'),
    url(r'^edit/i/(\d*)/save/$', 'recipes.views.save_incomplete_recipe', name='save_incomplete_recipe'),
                       
    url(r'^ajax/edit/(\d*)/$', 'recipes.views.ajax_edit_recipe', name='ajax_edit_recipe'),
    url(r'^ajax/edit/i/(\d*)/$', 'recipes.views.ajax_edit_recipe', kwargs={'incomplete': True},
        name='ajax_edit_incomplete_recipe'),
    
    
#     url(r'^add/$', EditRecipeWizard.as_view(EditRecipeWizard.FORMS), name='add_recipe'),
#     url(r'^edit/(?P<recipe_id>\d+)/$', EditRecipeWizard.as_view(EditRecipeWizard.FORMS), name='edit_recipe'),
    url(r'^delete/(\d*)/$', 'recipes.views.delete_recipe', name='delete_recipe'),
    url(r'^delete/i/(\d*)/$', 'recipes.views.delete_recipe', kwargs={'incomplete': True},
        name='delete_incomplete_recipe'),
    
    # Upload a recipe image
    url(r'^ajax/img/(\d+)/$', 'recipes.views.ajax_upload_recipe_image', name='ajax_upload_recipe_image'),
    url(r'^ajax/img/f/(\d+)/$', 'recipes.views.ajax_finish_recipe_image', name='ajax_finish_recipe_image'),
    
    # Statistical data about recipes
    url(r'^data/fpevo/(\d+)/$', 'recipes.views.get_recipe_footprint_evolution', name='graph_rfe'),
    # Unused for now
#     url(r'^data/fpdist/(\d+)/(\d+)/(\d+)/$', 'recipes.views.get_recipe_footprint_distribution', name='graph_rfd'),
#     url(r'^data/fprel/$', 'recipes.views.get_relative_footprint'),
    
    url(r'^markdownpreview/$', 'recipes.views.ajax_markdown_preview'),
)
