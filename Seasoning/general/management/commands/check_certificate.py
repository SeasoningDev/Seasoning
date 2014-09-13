from django.core.management.base import NoArgsCommand
import os, datetime
from django.core.mail.message import EmailMultiAlternatives

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
        subject = 'Seasoning certificaten gaan vervallen'
        message_text = 'De SSL certificaten van Seasoning gaan binnen %s dagen vervallen. Gelieve deze te vervangen. (sh renew_certificates.sh)' % (cert_end_date.date() - datetime.date.today()).days
        
        msg = EmailMultiAlternatives(subject, message_text, 'noreply@seasoning.be', ['admin@seasoning.be'])
        msg.send()

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        This does what you expect
        
        """
        check_certificate()