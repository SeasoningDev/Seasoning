from django.db import models
from datetime import datetime

class RequestLog(models.Model):
    
    line = models.PositiveIntegerField()
    
    time = models.DateTimeField()
    minute = models.CharField(max_length=12, editable=False)
    
    pid = models.PositiveIntegerField()
    wid = models.PositiveSmallIntegerField()
    
    ip = models.IPAddressField()
    user_agent = models.CharField(max_length=200)
    
    method = models.CharField(max_length=10)
    protocol = models.CharField(max_length=20)
    uri = models.CharField(max_length=100)
    status = models.PositiveSmallIntegerField()
    referer = models.CharField(max_length=200)
    
    msec = models.PositiveIntegerField()
    size = models.PositiveIntegerField()
    
    vsz = models.PositiveIntegerField()
    rss = models.PositiveIntegerField()
    
    def save(self, *args, **kwargs):
        self.minute = self.time.strftime('%Y%m%d%H%M')
        
        return models.Model.save(self, *args, **kwargs)