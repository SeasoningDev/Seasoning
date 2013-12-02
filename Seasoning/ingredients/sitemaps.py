from django.contrib import sitemaps
from django.core.urlresolvers import reverse
from ingredients.models import Ingredient

class IngredientViewsSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    
    def items(self):
        return Ingredient.objects.filter(accepted=True).values('id')
    
    def location(self, item):
        return reverse('view_ingredient', args=(item['id'],))