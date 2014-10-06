from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import re
import hashlib
from django.template import loader
from django.core.mail.message import EmailMultiAlternatives
import os
from email.mime.image import MIMEImage

def validate_image_size(fieldfile_obj):
    try:
        file_size = fieldfile_obj.file.size
    except IOError:
        return
    size_limit = settings.MAX_UPLOAD_SIZE
    if file_size > size_limit:
        raise ValidationError(_('Max file size is %sMB') % str(size_limit/(1024*1024)))

def all_templates(filter_with='', filter_without=''):
    from django.template.loaders.app_directories import app_template_dirs
    
    tid = 0
    templates = []
    for template_dir in (settings.TEMPLATE_DIRS + app_template_dirs):
        for cdir, _, filenames in os.walk(template_dir):
            for filename in filenames:
                full_path = os.path.join(cdir, filename)
                
                if not re.match('.*%s.*' % filter_with, full_path):
                    continue
                if re.match('.*%s.*' % filter_without, full_path):
                    continue
                
                rel_path = full_path.split('/templates/')[1]
                name = rel_path.split('/')[-1].split('.')[0]
                ctype = rel_path.split('.')[-1]
                templates.append({'name': name, 'path': rel_path,
                                  'id': tid, 'type': ctype})
                tid += 1
                                  
    return templates

def send_seasoning_email(subject_template, text_template, html_template, template_context,
                         from_email, to_emails):
    subject = loader.render_to_string(subject_template, template_context)
    
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    
    # Render message templates
    message_text = loader.render_to_string(text_template, template_context)
    message_html = loader.render_to_string(html_template, template_context)            
    
    
    msg = EmailMultiAlternatives(subject, message_text, from_email, to_emails)
    # Attach html message
    msg.attach_alternative(message_html, "text/html")
    
    msg.mixed_subtype = 'related'

    # Embed seasoning logo in email
    fp = open(settings.SMALL_LOGO_FILE, 'rb')
    msg_img = MIMEImage(fp.read())
    fp.close()
    msg_img.add_header('Content-ID', '<{}>'.format('logo.png'))
    msg.attach(msg_img)
    
    msg.send()