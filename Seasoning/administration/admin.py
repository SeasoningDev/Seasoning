'''
Created on Jul 7, 2015

@author: joep
'''
from django.contrib import admin
from administration.models import RequestLog

class SeasoningAdminSite(admin.AdminSite):
    pass

seasoning_admin_site = SeasoningAdminSite()


seasoning_admin_site.register(RequestLog)