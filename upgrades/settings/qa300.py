from common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',    # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'upgrade_path_portal',           # Or path to database file if using sqlite3.
        'USER': 'ssota_admin',                # Not used with sqlite3.
        'PASSWORD': 'ssota_23ad1',              # Not used with sqlite3.
        'HOST': 'db01.ssota.qa.blurdev.com', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                          # Set to empty string for default. Not used with sqlite3.
        }
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
STATS = restends.QA300STATS
TIMELINE = restends.QA300TIMELINE
PUBLISHEDPATH = restends.QA300OSMSUPS

DEFAULT_POLLING_INTERVAL = 360
