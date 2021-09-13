from common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'upgrade_path_portal',           # Or path to database file if using sqlite3.
        'USER': 'ssota_admin',                # Not used with sqlite3.
        'PASSWORD': 'tH8WA4rU',              # Not used with sqlite3.
        'HOST': 'db-vip01.mcloud401.blur.svcmot.com', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                          # Set to empty string for default. Not used with sqlite3.
        }
}

# Database cascade setting. The default setting is CASCADE.
from django.db import models
ON_DELETE = models.PROTECT

# Our portal and/or upgrade path related settings
import restends
LISTUM = restends.PRODILC_LISTUM
GETUM  = restends.PRODILC_GETUM
LISTPM = restends.PRODILC_PMGETPACKAGES
GETPACKAGEBINARIES = restends.PRODILC_PMGETBINARIES
POSTPATH = restends.PRODILC_GETUM
DEVICEEVENTS = restends.PRODILC_DEVICEEVENTS
LISTOFELIGIBLEDEVICE = restends.PRODILC_LISTOFELIGIBLEDEVICE
TLMSLISTS = restends.PRODILC_TLMSLISTS
TLMSTARGETS = restends.PRODILC_TLMSTARGETS
TLMSMATCH = restends.PRODILC_TLMSMATCH
TLMSCHECK = restends.PRODILC_TLMSCHECK
STATS = restends.PRODILC_STATS
TIMELINE = restends.PRODILC_TIMELINE
PUBLISHEDPATH = restends.PRODILC_OSMSUPS

DEFAULT_POLLING_INTERVAL = 86400
