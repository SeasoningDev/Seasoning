from django.core.management.base import NoArgsCommand
from django.conf import settings
import os
from django.template.loader import render_to_string

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        This command renders the infrastructure templates with the necessary context
        and puts them in place
        
        """
        if not os.path.exists('/etc/cron.daily'):
            print('/etc/cron.daily does not exist. Cannot install cron scripts')
            return
        
        with open('/etc/cron.daily/seasoning_backup_db.sh', 'w+') as f:
            f.write(render_to_string('infrastructure/cron/backup_db.sh.template', context={'settings': settings}))
            
        print('Updated Database backup script at /etc/cron.daily/seasoning_backup_db.sh')