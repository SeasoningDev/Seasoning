from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.template.loaders.app_directories import app_template_dirs
import re

def validate_image_size(fieldfile_obj):
    try:
        file_size = fieldfile_obj.file.size
    except IOError:
        return
    size_limit = settings.MAX_UPLOAD_SIZE
    if file_size > size_limit:
        raise ValidationError(_('Max file size is %sMB') % str(size_limit/(1024*1024)))

def all_templates(filter=''):
    
    import os
    
    template_files = []
    for template_dir in (settings.TEMPLATE_DIRS + app_template_dirs):
        for dir, dirnames, filenames in os.walk(template_dir):
            for filename in filenames:
                full_path = os.path.join(dir, filename)
                if not re.match('.*%s.*' % filter, full_path):
                    continue
                rel_path = full_path.split('/templates/')[1]
                template_files.append(rel_path)
    return template_files