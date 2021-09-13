from common import *

DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'device_cfg_portal',                      # Or path to database file if using sqlite3.
        'USER': 'root',                     # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                    # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                         # Set to empty string for default. Not used with sqlite3.
    }
}


LOGGING['handlers']['file'] = {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/tmp/portal.out',
            'maxBytes': 1024, # 1 KB
            'backupCount': 2,
            'formatter': 'verbose',
        }
LOGGING['handlers']['console'] = {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }

CAS_SERVER_URL = 'https://accounts-qa300.blurdev.com/ssoauth/'

# Database cascade setting. The default setting is CASCADE.
from django.db import models
ON_DELETE = models.PROTECT

# Our portal and/or upgrade path related settings
import restends
LISTUM = restends.QA300LISTUM
GETUM  = restends.QA300GETUM
LISTPM = restends.QA300PMGETPACKAGES
GETPACKAGEBINARIES = restends.QA300PMGETBINARIES
POSTPATH = restends.QA300GETUM
DEVICEEVENTS = restends.QA300DEVICEEVENTS
LISTOFELIGIBLEDEVICE = restends.QA300LISTOFELIGIBLEDEVICE
TLMSLISTS = restends.QA300TLMSLISTS
TLMSTARGETS = restends.QA300TLMSTARGETS
TLMSMATCH = restends.QA300TLMSMATCH
TLMSCHECK = restends.QA300TLMSCHECK
STATS = restends.QA300STATS                 # hardcoded to QA300 SUP
TIMELINE = restends.QA300TIMELINE
PUBLISHEDPATH = restends.QA300OSMSUPS

DEFAULT_POLLING_INTERVAL = 3601
