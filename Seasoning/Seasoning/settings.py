"""
Copyright 2012, 2013 Driesen Joep

This file is part of Seasoning.

Seasoning is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Seasoning is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Seasoning.  If not, see <http://www.gnu.org/licenses/>.
    
"""
# Django settings for Seasoning project.
import os
from Seasoning import secrets

# Debug settings
DEBUG = secrets.DEBUG
TEMPLATE_DEBUG = secrets.DEBUG

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost', 'www.seasoning.be', 'seasoning.be']

# The directory containing this file
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# The file to which the database backed up should be written
DB_BACKUP_FILE = os.path.join(BASE_DIR, '../../seasoning_db.bak')

ADMINS = (
    ('Joep Driesen', 'joeper_100@hotmail.com'),
    ('Bram Somers', 'somersbram@gmail.com'),
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

# Email configuration
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

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

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
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

PIPELINE_CSS = {
    'global': {
        'source_filenames': {
            'css/base/reset.scss',
            'css/base/global.scss',
            'css/base/skeleton.scss',
            'css/base/base.scss',
            'css/includes/*.scss',
            'css/plugins/*.scss',
        },
        'output_filename': 'css/global.css',
    },
    'general': {
        'source_filenames': {
            'css/contribute/*.scss',
            'css/general/*.scss',
        },
        'output_filename': 'css/general.css',
    },
    'authentication': {
        'source_filenames': {
            'css/authentication/*.scss',
        },
        'output_filename': 'css/authentication.css',
    },
    'ingredients': {
        'source_filenames': {
            'css/ingredients/*.scss',
        },
        'output_filename': 'css/ingredients.css',
    },
    'recipes': {
        'source_filenames': {
            'css/recipes/*.scss',
        },
        'output_filename': 'css/recipes.css',
    },
    'faq': {
        'source_filenames': {
            'css/faq/*.scss',
        },
        'output_filename': 'css/faq.css',
    },
    'news': {
        'source_filenames': {
            'css/news/*.scss',
        },
        'output_filename': 'css/news.css',
    },
}

PIPELINE_COMPILERS = (
  'pipeline.compilers.sass.SASSCompiler',
)

PIPELINE_SASS_BINARY = secrets.SASS_BINARY
PIPELINE_SASS_ARGUMENTS = '--update --force --load-path %s/css/imports/' % STATIC_ROOT

PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.cssmin.CSSMinCompressor'
PIPELINE_CSSMIN_BINARY = secrets.PIPELINE_CSSMIN_BINARY
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.jsmin.JSMinCompressor'

MARKITUP_FILTER = ('markdown.markdown', {'safe_mode': True})

JQUERY_URL = None

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
)


MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
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
    'django.contrib.comments',
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
    'news',
    
    # Admin
    'django.contrib.admin',
    
    # Misc
    'imagekit',
    'pipeline',
    'markitup',
)

AUTH_USER_MODEL = 'authentication.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'authentication.backends.GoogleAuthBackend',
    'authentication.backends.FacebookAuthBackend',
)

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
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
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
LOGIN_URL = '/login/'

# The URL where requests are redirected after login when the contrib.auth.login view gets no next parameter.
LOGIN_REDIRECT_URL = '/'

# Used by the authentication. Defines how many days an unactivated accounts will be stored in the database at the least.
ACCOUNT_ACTIVATION_DAYS = 7

# Registration is closed during development
# REGISTRATION_OPEN = False

# Django secret key
SECRET_KEY = secrets.SECRET_KEY


# Django-recaptcha
RECAPTCHA_PUBLIC_KEY = '6LcsROkSAAAAAE9JICOK0cLhDYWmpMRpOa7LNBWO'
RECAPTCHA_PRIVATE_KEY = secrets.RECAPTCHA_PRIVATE_KEY
RECAPTCHA_USE_SSL = True

FACEBOOK_APP_ID = secrets.FACEBOOK_APP_ID
FACEBOOK_SECRET = secrets.FACEBOOK_SECRET
GOOGLE_APP_ID = secrets.GOOGLE_APP_ID
GOOGLE_SECRET = secrets.GOOGLE_SECRET

DDF_DEFAULT_DATA_FIXTURE = 'Seasoning.utils.UserNamesOverwriter'

# If no MySQL server is available for testing, you might want to us sqlite. This
# will cause certain tests depending on MySQL fail. Set this setting to True to
# skip these tests when an sqlite backend is in use.
SKIP_MYSQL_TESTS = True
