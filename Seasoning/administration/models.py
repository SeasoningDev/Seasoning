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
    
    def distinct_ips(self, start_time, end_time):
        requests_no_admin = RequestLog.objects.exclude(uri__contains='admin').exclude(user_agent__iexact='-').exclude(user_agent__icontains='googlebot').exclude(user_agent__icontains='slurp').exclude(user_agent__icontains='yandexbot').exclude(user_agent__icontains='bingbot').exclude(user_agent__icontains='facebot').exclude(user_agent__icontains='twitterbot')
        request_in_timeframe = requests_no_admin.filter(time__gte=start_time, time__lte=end_time).order_by('time')
        
        distinct_ips = request_in_timeframe.extra({'date':"date(time)"}).values('date', 'ip').order_by('date').distinct()
        
        days = []
        for log in distinct_ips:
            if len(days) <= 0 or log['date'] != days[-1]['date']:
                days.append({'date': log['date'],
                             'count': 0,
                             'ips': []})
            
            days[-1]['count'] += 1
            days[-1]['ips'].append(log['ip'])
        
        return days
    
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