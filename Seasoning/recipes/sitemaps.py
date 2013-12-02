from django.contrib import sitemaps
from django.core.urlresolvers import reverse
from recipes.models import Recipe

class RecipeViewsSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    
    def items(self):
        return Recipe.objects.filter(accepted=True).values('id')
    
    def location(self, item):
        return reverse('view_recipe', args=(item['id'],))