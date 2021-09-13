from common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'upgrade_path_portal',           # Or path to database file if using sqlite3.
        'USER': 'ssota_admin',                # Not used with sqlite3.
        'PASSWORD': 'ssota_23ad1',              # Not used with sqlite3.
        'HOST': 'db01.ssota.sdc.blurdev.com', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                          # Set to empty string for default. Not used with sqlite3.
        }
}

# Database cascade setting. The default setting is CASCADE.
from django.db import models
ON_DELETE = models.PROTECT

# Our portal and/or upgrade path related settings
import restends
LISTUM = restends.SDC100LISTUM
GETUM  = restends.SDC100GETUM
LISTPM = restends.SDC100PMGETPACKAGES
GETPACKAGEBINARIES = restends.SDC100PMGETBINARIES
POSTPATH = restends. SDC100GETUM
DEVICEEVENTS = restends.SDC100DEVICEEVENTS
LISTOFELIGIBLEDEVICE = restends.SDC100LISTOFELIGIBLEDEVICE
TLMSLISTS = restends.SDC100TLMSLISTS
TLMSTARGETS = restends.SDC100TLMSTARGETS
TLMSMATCH = restends.SDC100TLMSMATCH
STATS = restends.SDC100STATS
TIMELINE = restends.SDC100TIMELINE
PUBLISHEDPATH = restends.SDC100OSMSUPS

DEFAULT_POLLING_INTERVAL = 3601
