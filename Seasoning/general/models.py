from django.db import models

class StaticPage(models.Model):
    
    class Meta:
        db_table = 'staticpage'
        
    name = models.CharField(max_length=50, unique=True)
    url = models.CharField(max_length=100, unique=True)
    
    body_html = models.TextField()
    
    last_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.name