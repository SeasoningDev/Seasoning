from django.shortcuts import render, redirect
from logs import parse_uwsgi_log
from django.core.urlresolvers import reverse
from django.core import serializers
from logs.models import RequestLog
import datetime
from django.db.models.aggregates import Count, Avg
import json
from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def parse_logs(request):
    return redirect(reverse('home'))

def view_logs(request):
    parse_uwsgi_log()
#     hits = RequestLog.objects.page_hits()
#     
#     return render(request, 'logs/view_logs.html', hits)
    
    return render(request, 'logs/view_logs.html')

@csrf_exempt
def ajax_site_wide_history(request):
    if not request.is_ajax() or request.method != 'POST':
        raise PermissionDenied()
    
    days = request.POST.get('days', None)
    interval = request.POST.get('interval', None)
    
    kwargs = {}
    if days is not None:
        kwargs['days'] = int(days)
    if interval is not None:
        kwargs['interval_min'] = int(interval)
    
    history_data = RequestLog.objects.history(**kwargs)
    history_data_json = json.dumps(history_data)
    
    return HttpResponse(history_data_json, content_type='application/javascript')
