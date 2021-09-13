from common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'upgrade_path_portal',           # Or path to database file if using sqlite3.
        'USER': 'up_portal_user',                # Not used with sqlite3.
        'PASSWORD': '769upgrade_9',              # Not used with sqlite3.
        'HOST': 'db01.ssota.sdc200.blurdev.com', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                          # Set to empty string for default. Not used with sqlite3.
        }
}

# Database cascade setting. The default setting is CASCADE.
from django.db import models
ON_DELETE = models.PROTECT

# Our portal and/or upgrade path related settings
import restends
LISTUM = restends.SDC200LISTUM
GETUM  = restends.SDC200GETUM
LISTPM = restends.SDC200PMGETPACKAGES
GETPACKAGEBINARIES = restends.SDC200PMGETBINARIES
POSTPATH = restends.SDC200GETUM
DEVICEEVENTS = restends.SDC200DEVICEEVENTS
LISTOFELIGIBLEDEVICE = restends.SDC200LISTOFELIGIBLEDEVICE
TLMSLISTS = restends.SDC200TLMSLISTS
TLMSTARGETS = restends.SDC200TLMSTARGETS
TLMSMATCH = restends.SDC200TLMSMATCH
TLMSCHECK = restends.SDC200TLMSCHECK
STATS = restends.SDC200STATS
TIMELINE = restends.SDC200TIMELINE
PUBLISHEDPATH = restends.SDC200OSMSUPS

DEFAULT_POLLING_INTERVAL = 3601
