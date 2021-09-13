from common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'upgrade_path_portal',           # Or path to database file if using sqlite3.
        'USER': 'ssota_admin',                # Not used with sqlite3.
        'PASSWORD': 'tH8WA4rU',              # Not used with sqlite3.
        'HOST': 'db01.mcloud101.blur.svcmot.com', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                          # Set to empty string for default. Not used with sqlite3.
        }
}

# Database cascade setting. The default setting is CASCADE.
from django.db import models
ON_DELETE = models.PROTECT

# Our portal and/or upgrade path related settings
import restends
LISTUM = restends.PRODLISTUM
GETUM  = restends.PRODGETUM
LISTPM = restends.PRODPMGETPACKAGES
GETPACKAGEBINARIES = restends.PRODPMGETBINARIES
POSTPATH = restends.PRODGETUM
DEVICEEVENTS = restends.PRODDEVICEEVENTS
LISTOFELIGIBLEDEVICE = restends.PRODLISTOFELIGIBLEDEVICE
TLMSLISTS = restends.PRODTLMSLISTS
TLMSTARGETS = restends.PRODTLMSTARGETS
TLMSMATCH = restends.PRODTLMSMATCH
TLMSCHECK = restends.PRODTLMSCHECK
STATS = restends.PRODSTATS
TIMELINE = restends.PRODTIMELINE
PUBLISHEDPATH = restends.PRODOSMSUPS

DEFAULT_POLLING_INTERVAL = 86400
