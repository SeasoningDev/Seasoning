"""
Copyright 2012, 2013 Driesen Joep

This file is part of Seasoning.

Seasoning is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Seasoning is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Seasoning.  If not, see <http://www.gnu.org/licenses/>.
    
"""
import time
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django import forms
from django.http.response import Http404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from general.forms import ContactForm
from general.models import StaticPage, RecipeOfTheWeek
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from ingredients.models import Ingredient
import re

def home(request):
    if request.user.is_authenticated():
        recipes_otw = RecipeOfTheWeek.objects.select_related('recipe').all().order_by('veganism')
        try:
            return render(request, 'homepage_logged_in.html', {'ven_recipe_otw': recipes_otw[2].recipe,
                                                               'veg_recipe_otw': recipes_otw[1].recipe,
                                                               'nveg_recipe_otw': recipes_otw[0].recipe})
        except IndexError:
            return render(request, 'homepage_logged_in.html')
    return render(request, 'homepage_not_logged_in.html')

def contribute(request):
    return render(request, 'contribute/contribute.html')

def donate(request):
    financial_reports_dir = '%s/docs/financial' % settings.STATIC_ROOT
    files = os.listdir(financial_reports_dir)
    financial_reports = []
    for thisfile in files:
        if re.match(r'^[^\.]*\.pdf$', thisfile):
            financial_reports.append(thisfile)
    return render(request, 'contribute/donate.html', {'financial_reports': financial_reports})

def donate_success(request):
    return render(request, 'contribute/donate_success.html')

def static_page(request, url):
    static_page = get_object_or_404(StaticPage, url=url)
    return render(request, 'static_page.html', {'page_info': static_page})

TYPES = {'info': {'title': 'Informatie, vragen en suggesties',
                  'email': 'info@seasoning.be'},
         'press': {'title': 'Media en partnerships',
                  'email': 'bram@seasoning.be'},
         'abuse': {'title': 'Technische problemen of misbruik',
                  'email': 'joep@seasoning.be'},}
def contact_form(request, contact_type):
    if contact_type not in TYPES:
        raise Http404
    
    if request.method == 'POST':
        form = ContactForm(request.POST, logged_in=request.user.is_authenticated())
        
        if form.is_valid():
            if request.user.is_authenticated():
                email = request.user.email
            else:
                email = form.fields['your_email']
            
            ctx_dict = {'type': TYPES[contact_type]['title'],
                        'email': email,
                        'subject': form.cleaned_data['subject'],
                        'message': form.cleaned_data['message']}
            
            # Email subject *must not* contain newlines
            subject = ''.join(form.cleaned_data['subject'])
            
            message_text_to_us = render_to_string('emails/contact_form_email.txt',
                                                  ctx_dict)
            message_text_feedback = render_to_string('emails/contact_form_autoreply.txt')
    
            send_mail('Contact van gebruiker: %s' % subject, message_text_to_us, 
                      email,
                      [TYPES[contact_type]['email']], fail_silently=True)
            send_mail('Contact met Seasoning.be', message_text_feedback, 
                      'noreply@seasoning.be',
                      [email], fail_silently=True)
            
            messages.add_message(request, messages.INFO, _('Your contact form was submitted succesfully.'))
            
            return redirect('/')
    else:
        form = ContactForm(logged_in=request.user.is_authenticated())
    
    return render(request, 'contact_form.html', {'form': form,
                                                 'contact_type': TYPES[contact_type]['title']})
    
@staff_member_required
def backup_db(request):
    '''
    Backup the Seasoning Database to disk
    '''
    db = settings.DATABASES['default']
    filename = "/backups/mysql/%s-%s.sql.bzip2" % (db['NAME'], time.strftime('%Y-%m-%d'))
    cmd = 'mysqldump --opt -u %s -p%s -e -c %s | bzip2 -c > %s' % (db['USER'], db['PASSWORD'], db['NAME'], filename)
    os.popen(cmd)
    
    return redirect(home)

@staff_member_required
def upload_static_image(request):
    """
    Upload a picture into the static folder
    
    """
    class UploadStaticImageForm(forms.Form):
        image = forms.FileField()
    
    static_img_dir = '%s/img/static' % settings.STATIC_ROOT
    
    def handle_uploaded_file(f):
        with open('%s/%s' % (static_img_dir, f.name), 'wb+') as destination:
            for chunck in f.chunks():
                destination.write(chunck)
    
    if request.method == 'POST':
        form = UploadStaticImageForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['image'])
            return redirect('/admin/')
    else:
        form = UploadStaticImageForm()
        
    images = os.listdir(static_img_dir)
    
    return render(request, 'admin/upload_image.html', {'form': form,
                                                       'images': images})
    
# TEST VIEWS FOR TEMPLATE INSPECTION
def test_500(request):
    if not request.user.is_staff:
        raise Http404
    return 1/0