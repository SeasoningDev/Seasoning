from django.db import models
import datetime
import json
from django.db.models.aggregates import Count, Avg

class RequestLogManager(models.Manager):
    
    def history(self, start_time, end_time):
        requests_no_admin = RequestLog.objects.exclude(uri__contains='admin')
        request_in_timeframe = requests_no_admin.filter(time__gte=start_time, time__lte=end_time).order_by('time')
        
        history = request_in_timeframe.extra(select={'timestr':"to_char(time, 'YYYY-MM-DD HH24:MI:SS')"}).values('timestr', 'ip')
        
        return history
        
    
    def page_hits(self, cutoff=20, days=None, order_by_responsetime=True):
        # TODO: implement uri filtering possibility (such as no admin pages)
        logs = self.exclude(status=500)
        
        if days is not None:
            logs = logs.filter(time__gte=(datetime.datetime.today() - datetime.timedelta(days=days)))
        
        logs = logs.values('uri').annotate(hits=Count('time')).annotate(response_time=Avg('msec'))
        
        if order_by_responsetime:
            logs = logs.order_by('-response_time')
        else:
            logs = logs.order_by('-hits')
            
        logs = logs[:cutoff]
        
        pages = []
        hits = []
        response_time = []
        for log in logs:
            pages.append(log['uri'])
            hits.append(log['hits'])
            response_time.append(log['response_time'])
        return {'pages': json.dumps(pages),
                'hits': json.dumps(hits),
                'resp_time': json.dumps(response_time)}
    
class RequestLog(models.Model):
    
    objects = RequestLogManager()
    
    time = models.DateTimeField()
    minute = models.CharField(max_length=12, editable=False)
    
    pid = models.PositiveIntegerField()
    wid = models.PositiveSmallIntegerField()
    
    ip = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=300)
    
    method = models.CharField(max_length=10)
    protocol = models.CharField(max_length=20)
    uri = models.CharField(max_length=300)
    uri_params = models.TextField()
    status = models.PositiveSmallIntegerField()
    referer = models.CharField(max_length=300)
    referer_params = models.TextField()
    
    msec = models.PositiveIntegerField()
    size = models.PositiveIntegerField()
    
    vsz = models.PositiveIntegerField()
    rss = models.PositiveIntegerField()
    
    def __str__(self):
        return 'Log entry: {}'.format(self.time.strftime('%x %X'))
    
    def save(self, *args, **kwargs):
        self.minute = self.time.strftime('%Y%m%d%H%M')
        
        if '?' in self.uri:
            self.uri_params = self.uri.split('?')[1]
        self.uri = self.uri.split('?')[0]
            
        if '?' in self.referer:
            self.referer_params = self.referer.split('?')[1]
        self.referer = self.referer.split('?')[0]
        
        return models.Model.save(self, *args, **kwargs)