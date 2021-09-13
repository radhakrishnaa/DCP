import socket


# Django settings for dcp project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG
HOST_NAME = socket.gethostname()
# Retrieving Database name based on the Hostname
# DB_HOST ='dbportalvip01.mcloud201.blur.svcmot.com'
# if "dc4" in HOST_NAME:
#    DB_HOST = 'dbportalvip01.mcloud401.blur.svcmot.com'
DB_HOST = 'dbportalvip01.mcloud201.blur.svcmot.com'
if "ilc" in HOST_NAME:
    DB_HOST = 'dbportalvip01.mcloud401.blur.svcmot.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'device_cfg_portal',
        'USER': 'dcp_user',
        'PASSWORD': 'zutha6A4',
        'HOST': DB_HOST,
        'PORT': '3306',
    }
}

# Database cascade setting. The default setting is CASCADE.
ON_DELETE = DeletionEffects.PROTECT

DEFAULT_CLOUD = 'prod'
CAS_SERVER_URL = 'https://motocastid.motorola.com/ssoauth/'
LOG_SETTINGS_CONFFILE = '/home/apache/gdicfg/dcp/config/logging_server.conf'
DONOT_PUBLISH = False
