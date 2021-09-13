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
LISTUM = restends.PRODVA3_LISTUM
GETUM  = restends.PRODVA3_GETUM
LISTPM = restends.PRODVA3_PMGETPACKAGES
GETPACKAGEBINARIES = restends.PRODVA3_PMGETBINARIES
POSTPATH = restends. PRODGETUM
DEVICEEVENTS = restends.PRODVA3_DEVICEEVENTS
LISTOFELIGIBLEDEVICE = restends.PRODVA3_LISTOFELIGIBLEDEVICE
TLMSLISTS = restends.PRODVA3_TLMSLISTS
TLMSTARGETS = restends.PRODVA3_TLMSTARGETS
TLMSMATCH = restends.PRODVA3_TLMSMATCH
TLMSCHECK = restends.PRODVA3_TLMSCHECK
STATS = restends.PRODVA3_STATS
TIMELINE = restends.PRODVA3_TIMELINE
PUBLISHEDPATH = restends.PRODVA3_OSMSUPS

DEFAULT_POLLING_INTERVAL = 86400
