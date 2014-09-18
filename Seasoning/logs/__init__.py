from django.conf import settings
from logs.models import RequestLog
import datetime

def parse_uwsgi_log():
    if settings.UWSGI_LOG_FILE is None:
        return False
    
    lf = open(settings.UWSGI_LOG_FILE, 'r')
    
    try:
        last_line_no = RequestLog.objects.latest('line')
    except RequestLog.DoesNotExist:
        last_line_no = -1
        
    for line_no, line in enumerate(lf):
        if line_no <= last_line_no:
            continue
        if not line.startswith('LOG'):
            continue
        
        _, timestamp, pid, wid, ip, user_agent, method, protocol, uri, status, msec, size, referer, vsz, rss = line.split('|')[0:15]
        time = datetime.datetime.utcfromtimestamp(int(timestamp))
        
        try:
            int(msec)
        except ValueError:
            msec = 0
        
        RequestLog(line=line_no, time=time, pid=pid, wid=wid, ip=ip, user_agent=user_agent,
                   method=method, protocol=protocol, uri=uri, status=status, 
                   referer=referer, msec=msec, size=size, vsz=vsz, rss=rss).save()
    
    lf.close()