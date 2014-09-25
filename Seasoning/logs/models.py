from django.db import models
import datetime
import json
from django.db.models.aggregates import Count, Avg

class RequestLogManager(models.Manager):
    
    def history(self, days=7, interval_min=5):
        """
        TODO: interval min omzetten naar een algemeen interval
        
        """
        logs = RequestLog.objects.filter(time__gte=(datetime.datetime.today() - datetime.timedelta(days=days))).order_by('time')
        
        times = []
        requests = []
        response_times = []
        distinct_ips = []
        ips = []
        cur_time = None
        for log in logs:
            while cur_time is None or (log.time - cur_time) > datetime.timedelta(minutes=interval_min):
                if cur_time is None:
                    cur_time = log.time.replace(minute=(log.time.minute - log.time.minute % interval_min), second=0, microsecond=0)
                else:
                    response_times[-1] = response_times[-1]/requests[-1] if requests[-1] > 0 else 0
                    cur_time += datetime.timedelta(minutes=5)
                
                requests.append(0)
                response_times.append(0)
                distinct_ips.append(0)
                ips = []
                times.append(cur_time.strftime('%d/%m/%y %H:%M'))
            
            requests[-1] += 1
            response_times[-1] += log.msec
            if log.ip not in ips:
                ips.append(log.ip)
                distinct_ips[-1] += 1
        
        response_times[-1] = response_times[-1]/requests[-1] if requests[-1] > 0 else 0
        
        return {'time_intervals': times,
                'requests': requests,
                'response_times': response_times,
                'distinct_ips': distinct_ips}
    
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
    
    def page_statistics(self, uri):
        pass
    
class RequestLog(models.Model):
    
    objects = RequestLogManager()
    
    line = models.PositiveIntegerField()
    
    time = models.DateTimeField()
    minute = models.CharField(max_length=12, editable=False)
    
    pid = models.PositiveIntegerField()
    wid = models.PositiveSmallIntegerField()
    
    ip = models.IPAddressField()
    user_agent = models.CharField(max_length=300)
    
    method = models.CharField(max_length=10)
    protocol = models.CharField(max_length=20)
    uri = models.CharField(max_length=300)
    status = models.PositiveSmallIntegerField()
    referer = models.CharField(max_length=300)
    
    msec = models.PositiveIntegerField()
    size = models.PositiveIntegerField()
    
    vsz = models.PositiveIntegerField()
    rss = models.PositiveIntegerField()
    
    def save(self, *args, **kwargs):
        self.minute = self.time.strftime('%Y%m%d%H%M')
        self.uri = self.uri.split('?')[0]
        self.referer = self.referer.split('?')[0]
        
        return models.Model.save(self, *args, **kwargs)