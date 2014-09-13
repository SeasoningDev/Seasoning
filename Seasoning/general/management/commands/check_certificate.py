from django.core.management.base import NoArgsCommand
from django.conf import settings
import os

def check_certificate():
    """
    Check the current certificate expiry date
    
    """
    cmd = 'openssl x509 -noout -in %s -dates' % settings.SSL_CERTIFICATE_FILE
    print(os.popen(cmd))

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        This command backs up all the media files and the database to the Seasoning Google Drive
        
        """
        check_certificate()