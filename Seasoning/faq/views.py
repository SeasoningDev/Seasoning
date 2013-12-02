from __future__ import absolute_import
from django.shortcuts import render
from .models import Topic

def topic_list(request):
    topics = Topic.objects.all().order_by('id').prefetch_related()
    return render(request, 'faq/topic_list.html', {'topics': topics})