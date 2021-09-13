import os.path
import logging.config

# Determine the site path based on the path to this settings file
SITEPATH = os.path.dirname(os.path.realpath(__file__))

# Django settings for dcp project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

USERADMINS = ('branta', 'pedroalo', 'wagner', 'rtalluri')

DATABASES = {
    'default': {
        # add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'
        'ENGINE': 'django.db.backends.mysql',
        # or path to database file if using sqlite3
        'NAME': 'device_cfg_portal',
        # not used with sqlite3
        'USER': 'root',
        # not used with sqlite3
        'PASSWORD': '',
        # set to empty string for localhost. Not used with sqlite3
        'HOST': '127.0.0.1',
        # set to empty string for default. Not used with sqlite3
        'PORT': '3306',
    }
}


class DeletionEffects(object):
    PROTECT = 'PROTECT'
    CASCADE = 'CASCADE'

ON_DELETE = DeletionEffects.PROTECT

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S %z'
DATE_FORMAT = '%Y-%m-%d %z'
TIME_FORMAT = '%H:%M:%S %z'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITEPATH, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'sefi+1x%kb4+n(^(ew%pux##*$qvrpzdcjgf*7b_wjn*wfh=$$'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django_cas.middleware.CASMiddleware',
    'api.csrf.DisableCSRF',
    'reversion.middleware.RevisionMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas.backends.CASBackend',
)

# CAS_SERVER_URL = 'https://motocastid-sdc100.blurdev.com/ssoauth/'
# CAS_SERVER_URL = 'https://motocastid.motorola.com/ssoauth/'

ROOT_URLCONF = 'dcp.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'dcp.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITEPATH, 'templates'),
)

ALLOWED_INCLUDE_ROOTS = (
    os.path.join(SITEPATH, 'static'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'rest_framework',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'util',
    'api',
    'south',
    'reversion',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
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
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

DEFAULT_CLOUD = 'qa300'

# Don't publish config to any cloud
DONOT_PUBLISH = False

LOGFILE = os.path.join(SITEPATH, 'logs/logfile.log')

DIFFSFILE = os.path.join(SITEPATH, 'logs/diffsfile.log')

LOG_SETTINGS_CONFFILE = None
DIFFSFILE_APPROVED = os.path.join(SITEPATH, 'logs/diffsfile_approved.log')
######################################################################
# Apply settings specific to the environment.
LOCAL_SETTINGS_CONF = os.path.join(SITEPATH, 'local_settings.conf')
with open(LOCAL_SETTINGS_CONF) as fh:
    exec(fh, globals(), globals())

if LOG_SETTINGS_CONFFILE:
    logging.config.fileConfig(os.path.join(SITEPATH, LOG_SETTINGS_CONFFILE))

######################################################################
# Change the ON_DELETE value to the real django value. This
# must be done after other DB configurations since it imports
# django.db.models, which makes use of the DB configuration values.
from django.db import models
ON_DELETE = models.__dict__[ON_DELETE]
