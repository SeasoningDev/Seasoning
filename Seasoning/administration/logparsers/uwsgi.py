'''
Created on 7-nov.-2015

@author: joep
'''
from django.conf import settings
from administration.models import RequestLog
import datetime
from django.utils.dateparse import parse_datetime

def parse_uwsgi_log():
    if settings.UWSGI_LOG_FILE is None:
        return False
    
    lf = open(settings.UWSGI_LOG_FILE, 'r')
    
    try:
        last_parse_time = RequestLog.objects.latest('time').time
    except RequestLog.DoesNotExist:
        last_parse_time = None
        
    for line in lf:
        if not line.startswith('LOG'):
            continue
        
        _, timestamp, pid, wid, ip, user_agent, method, protocol, uri, status, msec, size, referer, vsz, rss = line.split('|')[0:15]
        time = parse_datetime(datetime.datetime.utcfromtimestamp(int(timestamp)).strftime('%Y-%m-%d %XZ'))
        
        if last_parse_time is not None and last_parse_time >= time:
            continue
        
        try:
            int(msec)
        except ValueError:
            msec = 0
        
        RequestLog(time=time, pid=pid, wid=wid, ip=ip, user_agent=user_agent,
                   method=method, protocol=protocol, uri=uri, status=status, 
                   referer=referer, msec=msec, size=size, vsz=vsz, rss=rss).save()
    
    lf.close()
    