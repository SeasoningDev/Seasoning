from django.core.management.base import NoArgsCommand
import os, datetime
from django.core.mail import send_mail

def check_certificate():
    """
    Check the current certificate expiry date and mail the admin if it expires within 10 days
    
    """
    cmd = 'echo | openssl s_client -connect seasoning.be:443 2>/dev/null | openssl x509 -noout -dates'
    x = os.popen(cmd)
    x.readline()
    cert_end_date = x.readline().split('=')[1].split(' GMT')[0]
    cert_end_date = datetime.datetime.strptime(cert_end_date, '%b %d %H:%M:%S %Y')
    
    if (cert_end_date.date() - datetime.date.today()) < datetime.timedelta(days=10):
        send_mail('Seasoning certificaten gaan vervallen', 
                  'De SSL certificaten van Seasoning gaan binnen %s dagen vervallen. Gelieve deze te vervangen. (sh renew_certificates.sh)' % (cert_end_date.date() - datetime.date.today()).days, 
                  'cert_checker@seasoning.be',
                  ['admin@seasoning.be'], fail_silently=False)
            

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        This does what you expect
        
        """
        check_certificate()