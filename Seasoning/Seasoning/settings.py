"""
Django settings for Seasoning project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import Seasoning.settings_secrets as secret

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret.DJANGO_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = secret.DEBUG

ALLOWED_HOSTS = ['seasoning.be', '127.0.0.1', 'localhost']

# Determine if we are running in the test environment.
TEST = False
manage_command = [arg for arg in sys.argv if arg.find('manage.py') != -1]
if len(manage_command) != 0:
    command = sys.argv.index(manage_command[0]) + 1
    if command < len(sys.argv):
        TEST = sys.argv[command] == "test"


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'imagekit',
    'ingredients',
    'recipes',
    
    'administration',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'Seasoning.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'Seasoning', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'Seasoning', 'static'),
)

WSGI_APPLICATION = 'Seasoning.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

if TEST:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        },
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': secret.DB_NAME,
            'USER': secret.DB_USER,
            'PASSWORD': secret.DB_PASSWORD,
            'HOST': secret.DB_HOST,
            'PORT': secret.DB_PORT,

            'BACKUP_USER': secret.DB_BACKUP_USER,
            'BACKUP_DIR': secret.DB_BACKUP_DIR,
        },
    }


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'nl-be'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = secret.STATIC_ROOT

MEDIA_URL ='/media/'
MEDIA_ROOT = secret.MEDIA_ROOT

MEDIA_BACKUP_DIR = secret.MEDIA_BACKUP_DIR



MARKITUP_FILTER = ('markdown.markdown', {'safe_mode': True})



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
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
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

if DEBUG or TEST:
    UWSGI_LOG_FILE = os.path.join(BASE_DIR, secret.UWSGI_LOG_FILE)
else:
    UWSGI_LOG_FILE = secret.UWSGI_LOG_FILE
