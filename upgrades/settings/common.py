import os.path

# Determine the site path based on the path to this settigns file.
SITEPATH = os.path.abspath(os.path.join(os.path.dirname( os.path.realpath(__file__) ), '..'))

# Django settings for upgrades project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

USERADMINS = ( 'fkr684@motorola.com',)

AUTH_PROFILE_MODULE = "UserProfile"

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'sefi+1x%kb4+n(^(ew%pux##*$qvrpzdcjgf*7b_wjn*wfh=$$'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Los_Angeles'

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
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django_cas.middleware.CASMiddleware',
    'reversion.middleware.RevisionMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas.backends.CASBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth',
    )

CAS_SERVER_URL = 'https://accounts-sdc200.blurdev.com/ssoauth/'

ROOT_URLCONF = 'upgrades.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'upgrades.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
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
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'south',
    'reversion',
    'upgrades',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'file':{
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/portal/portal.out',
            'maxBytes': 1024*1024*100, # 100 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'upgrades.views': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'upgrades.dgcs': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'requests.packages.urllib3': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Service account private key -- guard it with your life
SERVICE_ACCOUNT_PK = '''-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDOxlzgplxAMJR+mZh7RMeoFnrWJojf/TzSUJ5E/TaieWSyh6RB
9HLRjoNwStmA7GLMQLiKoGwadxX6kQRGBwnh7mC38iqqmiB/u9QSbdadU3WNP4ma
Udqi1YhIlWj125a3GjkkHragxRWwjoZ6SfAmFHMCFhcIXkcsT0rO8G2gYQIDAQAB
AoGAEYxwMXis952n3J64fC24LCHMRwR6NVhOoyLIa955loxq6WPtotNWM0a/DPat
Qu3M7LzJbKp0wkI9EUjhbfgG9Iiw0sP+Vl9JK0wAWQ9x5JgCc9d1bY1g/TipnBJ5
lQ/O0qRcwl3t7MunNPgvLELajJvg1s9RknMv7fVEcA2ioOECQQDrEp8ROoOm9RyL
mfjOPkgezt8xd7yFEO3Ee7l9Fn84+sMWNw5HREeZXgVbN8wReCCLQzdCDtlRptzt
GQOB0mL9AkEA4S7S+QFZaZIvH9uayJtealytC+Tl3Q5xg/w7UpuTMyNXvy4Nnf31
rj+x2zSzd2VcC9Xqq+ESYsVDRP7UFOpKNQJBANXNdv29gbZdo1vZa/FxtjjHITsl
00IX1pnpihiaWJYjhUJ0SrlJAfIdELQZeLK+1qKzPNQJG2FnafL/2C/AgaUCQDKo
7h3HB+6QTLnGFhR7n8od/3BllrEcxr0CyfXTulIO6XbBTZ71u4fwHHtMZ/O8gfDH
t3vjrtc5ueCT0/LAouECQQCwAruFTukZTbGor4tkzwAIdx1pSROVtnvmq40/8oeo
h+/e+RHTCBhZG2vhWQnLJlpKclrp7GhkDgomg++6IxXl
-----END RSA PRIVATE KEY-----
'''

UPLOAD_CHUNKSIZE = 64 * 1024

BATCH_SIZE=10000;
