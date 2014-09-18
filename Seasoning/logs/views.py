from django.shortcuts import render, redirect
from logs import parse_uwsgi_log
from django.core.urlresolvers import reverse
from django.core import serializers
from logs.models import RequestLog
import datetime
from django.db.models.aggregates import Count, Avg
import json

def parse_logs(request):
    return redirect(reverse('home'))

def view_logs(request):
    parse_uwsgi_log()
    hits = RequestLog.objects.page_hits()
    
#     days = int(request.GET.get('days', 7))
#     interval = int(request.GET.get('interval', 5))
#     history = RequestLog.objects.history(days, interval)
    
    return render(request, 'logs/view_logs.html', hits)
