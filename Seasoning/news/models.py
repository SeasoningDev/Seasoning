from django.db import models
from django.contrib.auth import get_user_model
import time
from imagekit.models.fields import ProcessedImageField
from imagekit.processors.resize import ResizeToFill
import datetime
from django.utils.translation import ugettext_lazy as _

def get_image_filename(instance, old_filename):
    filename = str(time.time()) + '.png'
    return 'images/news/' + filename

class NewsItem(models.Model):
    
    class Meta:
        db_table = 'newsitem'
    
    author = models.ForeignKey(get_user_model())
    time_published = models.DateTimeField(auto_now_add=True)
    
    subject = models.CharField(max_length=300)
    content = models.TextField()
    image = ProcessedImageField(format='PNG', upload_to=get_image_filename, processors=[ResizeToFill(500, 500)],
                                help_text=_('An image of this news item.'))
    image_source = models.TextField(blank=True)
    
    visible = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.subject
    
    def save(self, *args, **kwargs):
        # Update the publish time if this item was previously invisible and has now been made visible
        if self.id:
            old_news = NewsItem.objects.get(id=self.id)
            if not old_news.visible and self.visible:
                self.time_published = datetime.datetime.now()
        return super(NewsItem, self).save(*args, **kwargs)
        
        
            
    
    
