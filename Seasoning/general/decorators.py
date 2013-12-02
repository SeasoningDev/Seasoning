from django.conf import settings
from django.utils.unittest.case import skip

def mysqldb_required(func):
    
    if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.mysql':
        if settings.SKIP_MYSQL_TESTS:
            @skip('This test requires a MySQL Database')
            def dummy(*args, **kwargs):
                pass
            return dummy
        
        def fail(*args, **kwargs):
            raise Exception('Please use a MySQL Database for this test')
        return fail
    return func