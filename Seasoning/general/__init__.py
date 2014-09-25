from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import re
import hashlib

def validate_image_size(fieldfile_obj):
    try:
        file_size = fieldfile_obj.file.size
    except IOError:
        return
    size_limit = settings.MAX_UPLOAD_SIZE
    if file_size > size_limit:
        raise ValidationError(_('Max file size is %sMB') % str(size_limit/(1024*1024)))

def all_templates(filter_with='', filter_without=''):
    import os
    from django.template.loaders.app_directories import app_template_dirs
    
    tid = 0
    templates = []
    for template_dir in (settings.TEMPLATE_DIRS + app_template_dirs):
        for dir, dirnames, filenames in os.walk(template_dir):
            for filename in filenames:
                full_path = os.path.join(dir, filename)
                
                if not re.match('.*%s.*' % filter_with, full_path):
                    continue
                if re.match('.*%s.*' % filter_without, full_path):
                    continue
                
                rel_path = full_path.split('/templates/')[1]
                name = rel_path.split('/')[-1].split('.')[0]
                type = rel_path.split('.')[-1]
                templates.append({'name': name, 'path': rel_path,
                                  'id': tid, 'type': type})
                tid += 1
                                  
    return templates