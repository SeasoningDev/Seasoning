from django.contrib import sitemaps
from general.models import StaticPage
from django.core.urlresolvers import reverse

class GeneralViewsSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'
    
    def items(self):
        return ['home', 'contribute', 'donate', 'faq']
    
    def location(self, item):
        return reverse(item)
    
class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return StaticPage.objects.all()

    def location(self, item):
        return '/%s/' % item.url
    
    def lastmod(self, item):
        return item.last_modified