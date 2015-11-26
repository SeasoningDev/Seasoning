from django.core.management.base import NoArgsCommand
from django.conf import settings
import os
from django.template.loader import render_to_string
import sys

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        """
        This command renders the infrastructure templates with the necessary context
        and puts them in place
        
        """
        if not os.path.exists('/etc/cron.daily'):
            print('/etc/cron.daily does not exist. Cannot install cron scripts')
            return
        
        backup_db_script = '/etc/cron.daily/seasoning_backup_db.sh'
        with open(backup_db_script, 'w+') as f:
            f.write(render_to_string('infrastructure/cron/backup_db.sh.template', context={'settings': settings}))
        make_executable(backup_db_script)
        
        print('Updated Database backup script at /etc/cron.daily/seasoning_backup_db.sh')
        
        backup_media_script = '/etc/cron.daily/seasoning_backup_media.sh'
        with open(backup_media_script, 'w+') as f:
            f.write(render_to_string('infrastructure/cron/backup_media.sh.template', context={'settings': settings}))
        make_executable(backup_media_script)
        
        print('Updated Media Files backup script at /etc/cron.daily/seasoning_backup_media.sh')
        
        update_seasoning_script = '/etc/cron.monthly/seasoning_update.sh'
        with open(update_seasoning_script, 'w+') as f:
            f.write(render_to_string('infrastructure/cron/update.sh.template', context={'PYTHON_EXE': sys.executable,
                                                                                        'settings': settings}))
        make_executable(update_seasoning_script)
            
        print('Updated Update script at /etc/cron.monthly/seasoning_update.sh')
        


def make_executable(filename):
    mode = os.stat(filename).st_mode
    mode |= (mode & 0o444) >> 2 # Copy R bits to X
    os.chmod(filename, mode)