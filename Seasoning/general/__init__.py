from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

def validate_image_size(fieldfile_obj):
    file_size = fieldfile_obj.file.size
    size_limit = settings.MAX_UPLOAD_SIZE
    if file_size > size_limit:
        raise ValidationError(_('Max file size is %sMB') % str(size_limit/(1024*1024)))