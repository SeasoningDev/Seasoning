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
import re
from general import all_templates, send_seasoning_email
from django.contrib.sites.models import RequestSite
from django.template.context import RequestContext
from django.core.mail.message import EmailMultiAlternatives

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
                email = form.cleaned_data['your_email']
            
            ctx_dict = {'type': TYPES[contact_type]['title'],
                        'email': email,
                        'subject': form.cleaned_data['subject'],
                        'message': form.cleaned_data['message']}
            
            # Send email to us
            subject_text_to_us = render_to_string('emails/contact_form_subject.txt',
                                                  ctx_dict)
            # Email subject *must not* contain newlines
            subject_text_to_us = ''.join(subject_text_to_us.splitlines())
            message_text_to_us = render_to_string('emails/contact_form_email.txt',
                                                  ctx_dict)
            send_mail(subject_text_to_us, message_text_to_us, 
                      'contact@seasoning.be',
                      [TYPES[contact_type]['email']], fail_silently=False)
            
            
            # Send confirmation email to user
            send_seasoning_email('emails/contact_form_autoreply_subject.txt', 
                                 'emails/contact_form_autoreply.txt', 
                                 'emails/contact_form_autoreply.html', 
                                 ctx_dict, 'noreply@seasoning.be', [email])
            
            messages.add_message(request, messages.INFO, _('Your contact form was submitted succesfully.'))
            
            return redirect('/')
    else:
        form = ContactForm(logged_in=request.user.is_authenticated())
    
    return render(request, 'contact_form.html', {'form': form,
                                                 'contact_type': TYPES[contact_type]['title']})

@staff_member_required
def upload_static_image(request):
    """
    Upload a picture into the static folder
    XtNbleXlMsq1GysQ4oSI
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
@staff_member_required
def email_preview(request, tid):
    class InvalidVarException(object):
        """
        Raise this exception if a variable is missing from the email template
        
        """
        def __mod__(self, missing):
            try:
                missing_str=unicode(missing)
            except:
                missing_str='Failed to create string representation'
            raise Exception('Unknown template variable %r %s' % (missing, missing_str))
        def __contains__(self, search):
            if search=='%s':
                return True
            return False
    
    try:
        templates = all_templates(filter_with='emails', filter_without='subject')
        for template in templates:
            if template['id'] == int(tid):
                break
        else:
            raise IndexError
    except IndexError:
        raise Http404
    
    global_context = {'uid': 1, 'token': '1-1',
                       'activation_key': 1,
                       'protocol': 'https', 'domain': 'www.seasoning.be',
                       'site': RequestSite(request),
                       'type': 'test', 'email': 'test', 'subject': 'test', 'message': 'test',
                       'request_string': 'test'}
    
    # Make temporary changes
    r = render_to_string(template['path'], global_context, context_instance=RequestContext(request))
    
    return render(request, 'admin/email_preview.html', {'template_html': r, 'is_text': '.txt' in template['path']})
    
@staff_member_required
def contact_overview(request):
    if not request.user.is_staff:
        raise Http404
    
    templates = all_templates(filter_with='emails', filter_without='subject')
    
    grouped_templates = {}
    for template in templates:
        if template['name'] in grouped_templates:
            grouped_templates[template['name']].insert(0, template)
        else:
            grouped_templates[template['name']] = [template]
    
    return render(request, 'admin/contact_overview.html', {'grouped_emails': grouped_templates.values()})
    
# TEST VIEWS FOR TEMPLATE INSPECTION
@staff_member_required
def test_500(request):
    return 1/0