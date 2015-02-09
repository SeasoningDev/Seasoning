# Django settings for Seasoning project.
import os
import sys
from django.core.exceptions import SuspiciousOperation

# Determine if we are running in the test environment.
TEST = False
manage_command = filter(lambda x: x.find('manage.py') != -1, sys.argv)
if len(manage_command) != 0:
    command = sys.argv.index(manage_command[0]) + 1
    if command < len(sys.argv):
        TEST = sys.argv[command] == "test"
        
# Determine if we are running a development version on localhost
LOCAL_TEST = len(sys.argv) > 1 and sys.argv[1] == 'runserver'
LOCAL_TEST = False

from Seasoning import secrets

# Debug settings
DEBUG = secrets.DEBUG
TEMPLATE_DEBUG = secrets.DEBUG

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost', 'www.seasoning.be', 'seasoning.be']

# The directory containing the source code
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The file to which the database backed up should be written
DB_BACKUP_FILE = os.path.join(BASE_DIR, '../../seasoning_db.bak')

# The file containing the small seasoning logo
SMALL_LOGO_FILE = os.path.join(BASE_DIR, 'general/static/img/logos/circle_leaf.png')

SESSION_COOKIE_DOMAIN = secrets.SESSION_COOKIE_DOMAIN

ADMINS = (
    ('Joep Driesen', 'joep.driesen@seasoning.be'),
)

MANAGERS = ADMINS

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': secrets.DATABASE_ENGINE, # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': secrets.DATABASE_NAME,                      # Or path to database file if using sqlite3.
        'USER': secrets.DATABASE_USER,                      # Not used with sqlite3.
        'PASSWORD': secrets.DATABASE_PASSWORD,                  # Not used with sqlite3.
        'HOST': secrets.DATABASE_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': secrets.DATABASE_PORT,                      # Set to empty string for default. Not used with sqlite3.
    }
}

DATABASE_DAILY_BACKUP_FILE = secrets.DATABASE_DAILY_BACKUP_FILE

# Email configuration
EMAIL_BACKEND = secrets.EMAIL_BACKEND
EMAIL_HOST = secrets.EMAIL_HOST
EMAIL_PORT = secrets.EMAIL_PORT
EMAIL_HOST_USER = secrets.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = secrets.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = secrets.EMAIL_USE_TLS
DEFAULT_FROM_EMAIL = 'activation@seasoning.be'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

LANGUAGES = (('nl', 'Dutch'),)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nl-be'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

SITE_ID = secrets.SITE_ID

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = secrets.MEDIA_URL

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = secrets.STATIC_URL

# During development, 
MEDIA_ROOT = secrets.MEDIA_ROOT
STATIC_ROOT = secrets.STATIC_ROOT

MEDIA_DAILY_BACKUP_FILE = secrets.MEDIA_DAILY_BACKUP_FILE

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# A tuple of callables that are used to populate the context in RequestContext. 
# These callables take a request object as their argument and return a dictionary 
# of items to be merged into the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    'django.contrib.messages.context_processors.messages',
    'Seasoning.local_test_context_processor',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
#     'pipeline.middleware.MinifyHTMLMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'Seasoning.urls'

# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
TEMPLATE_DIRS = (
    BASE_DIR + '/Seasoning/templates',
)

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    
    # Authentication:
    'django.contrib.auth',
    'authentication',
    'captcha',
    
    # Core functionality
    'general',
    'ingredients',
    'recipes',
    'faq',
    
    # Admin
    'django.contrib.admin',
    'logs',
    
    # Misc
    'imagekit',
    'pipeline',
    'markitup',
    'debug_toolbar'
)

AUTH_USER_MODEL = 'authentication.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'authentication.backends.GoogleAuthBackend',
    'authentication.backends.FacebookAuthBackend',
)

SERVER_EMAIL = 'server@seasoning.be'


def skip_suspicious_operations(record):
    if record.exc_info:
        exc_value = record.exc_info[1]
        if isinstance(exc_value, SuspiciousOperation):
            return False
        return True
  
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },
        'skip_suspicious_operations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': skip_suspicious_operations,
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', 'skip_suspicious_operations'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    }
}

# The URL where requests are redirected for login, especially when using the login_required() decorator.
LOGIN_URL = '/profile/login/'

# The URL where requests are redirected after login when the contrib.auth.login view gets no next parameter.
LOGIN_REDIRECT_URL = '/'

# Django secret key
SECRET_KEY = secrets.SECRET_KEY

# If no MySQL server is available for testing, you might want to us sqlite. This
# will cause certain tests depending on MySQL fail. Set this setting to True to
# skip these tests when an sqlite backend is in use.
SKIP_MYSQL_TESTS = True

MAX_UPLOAD_SIZE = 4*1024*1024


"""
Third Party Apps Settings
"""

# Used by the authentication. Defines how many days an unactivated accounts will be stored in the database at the least.
ACCOUNT_ACTIVATION_DAYS = 7

# Registration is closed during development
# REGISTRATION_OPEN = False



# Django-recaptcha
RECAPTCHA_PUBLIC_KEY = '6LcsROkSAAAAAE9JICOK0cLhDYWmpMRpOa7LNBWO'
RECAPTCHA_PRIVATE_KEY = secrets.RECAPTCHA_PRIVATE_KEY
RECAPTCHA_USE_SSL = True

FACEBOOK_APP_ID = secrets.FACEBOOK_APP_ID
FACEBOOK_SECRET = secrets.FACEBOOK_SECRET
GOOGLE_APP_ID = secrets.GOOGLE_APP_ID
GOOGLE_SECRET = secrets.GOOGLE_SECRET
GOOGLE_CREDS_FILE =  os.path.join(BASE_DIR, 'Seasoning', secrets.GOOGLE_CREDS_FILE)

DDF_DEFAULT_DATA_FIXTURE = 'Seasoning.utils.UserNamesOverwriter'



STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
if TEST:
    STATICFILES_STORAGE = 'pipeline.storage.NonPackagingPipelineStorage'

PIPELINE_CSS = {
    'global': {
        'source_filenames': (
#             'css/base/reset.scss',
            'css/base/global.scss',
#             'css/base/skeleton.scss',
            'css/base/base.scss',
            'css/base/forms.scss',
            'css/includes/*.scss',
            'css/plugins/*.scss',
        ),
        'output_filename': 'css/global.css',
    },
    'mobile': {
        'source_filenames': (
            'css/base/mobile.scss',
        ),
        'output_filename': 'css/mobile.css',
        'extra_context': {
            'media': 'all and (max-width: 767px)'
        }
    },
    'general': {
        'source_filenames': (
            'css/contribute/*.scss',
            'css/general/*.scss',
        ),
        'output_filename': 'css/general.css',
    },
    'authentication': {
        'source_filenames': (
            'css/authentication/*.scss',
        ),
        'output_filename': 'css/authentication.css',
    },
    'ingredients': {
        'source_filenames': (
            'css/ingredients/*.scss',
        ),
        'output_filename': 'css/ingredients.css',
    },
    'recipes': {
        'source_filenames': (
            'css/recipes/browse_recipes.scss',
            'css/recipes/edit_recipe.scss',
            'css/recipes/view_recipe.scss',
            'css/recipes/print_recipe.scss',
        ),
        'output_filename': 'css/recipes.css',
    },
    'faq': {
        'source_filenames': (
            'css/faq/*.scss',
        ),
        'output_filename': 'css/faq.css',
    },
}

PIPELINE_COMPILERS = (
  'pipeline.compilers.sass.SASSCompiler',
)

PIPELINE_SASS_BINARY = secrets.SASS_BINARY
PIPELINE_SASS_ARGUMENTS = '--update --force --load-path %s/css/imports/' % STATIC_ROOT

# PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.cssmin.CSSMinCompressor'
# PIPELINE_CSSMIN_BINARY = secrets.PIPELINE_CSSMIN_BINARY
PIPELINE_CSS_COMPRESSOR = None
# PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.jsmin.JSMinCompressor'
PIPELINE_JS_COMPRESSOR = None

MARKITUP_FILTER = ('markdown.markdown', {'safe_mode': True})

JQUERY_URL = None

INTERNAL_IPS = ('0.0.0.0',)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    #'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
)

def show_toolbar(request):
    if hasattr(request, 'hide_toolbar'):
        return False
    if request.user.is_staff:
        return True
    return False

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'Seasoning.settings.show_toolbar'
}

DEBUG_TOOLBAR_PATCH_SETTINGS = False

SSL_CERTIFICATE_FILE = secrets.SSL_CERTIFICATE_FILE

UWSGI_LOG_FILE = secrets.UWSGI_LOG_FILE

TEST_RUNNER = 'django.test.runner.DiscoverRunner'


# This is an array with, for each category (A+, A, B, C, D), the percentage of
# recipes with the lowest footprints that should fall under this category
# If a negative percentage is given, all recipes will fall under this category
#                              A+   A     B    C     D
RECIPE_CATEGORY_PERCENTAGES = [0.1, 0.25, 0.5, 0.75, -1]