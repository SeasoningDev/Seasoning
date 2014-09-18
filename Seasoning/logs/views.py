from django.shortcuts import render, redirect
from logs import parse_uwsgi_log
from django.core.urlresolvers import reverse
from django.core import serializers
from logs.models import RequestLog
import datetime
from django.db.models.aggregates import Count
import json

def parse_logs(request):
#     RequestLog.objects.all().delete()
    parse_uwsgi_log()
    return redirect(reverse('home'))

def view_logs(request):
    logs = RequestLog.objects.filter(time__gte=(datetime.datetime.today() - datetime.timedelta(days=7))).order_by('time')
    times = []
    requests = []
    response_time = []
    distinct_ips = []
    ips = []
    cur_time = None
    for log in logs:
        while cur_time is None or (log.time - cur_time) > datetime.timedelta(minutes=5):
            if cur_time is None:
                cur_time = log.time.replace(minute=(log.time.minute - log.time.minute % 5), second=0, microsecond=0)
            else:
                response_time[-1] = response_time[-1]/requests[-1] if requests[-1] > 0 else 0
                cur_time += datetime.timedelta(minutes=5)
            
            requests.append(0)
            response_time.append(0)
            distinct_ips.append(0)
            ips = []
            times.append(cur_time.strftime('%d/%m/%y %H:%M'))
        
        requests[-1] += 1
        response_time[-1] += log.msec
        if log.ip not in ips:
            ips.append(log.ip)
            distinct_ips[-1] += 1
    
    response_time[-1] = response_time[-1]/requests[-1] if requests[-1] > 0 else 0
    times_json = json.dumps(times)
    log_json = json.dumps(requests)
    msec_json = json.dumps(response_time)
    ips = json.dumps(distinct_ips)
    
    return render(request, 'logs/view_logs.html', {'times': times_json,
                                                   'json_log_data': log_json,
                                                   'msecs': msec_json,
                                                   'ips': ips})
