from django.contrib import sitemaps
from django.core.urlresolvers import reverse
from news.models import NewsItem

class NewsViewsSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    
    def items(self):
        return NewsItem.objects.filter(visible=True).values('id', 'time_published')
    
    def location(self, item):
        return reverse('view_news', args=(item['id'],))
    
    def lastmod(self, item):
        return item['time_published']