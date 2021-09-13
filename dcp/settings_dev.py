# Django settings for dcp project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Database cascade setting. The default setting is CASCADE.
ON_DELETE = DeletionEffects.CASCADE

DEFAULT_CLOUD = 'qa300'
# We need production SSO url for QA as QA version of SSO needs the HTTPS on QA
# machine which is not available
CAS_SERVER_URL = 'https://motocastid.motorola.com/ssoauth/'
# CAS_SERVER_URL = 'https://accounts-qa300.blurdev.com/ssoauth/'
LOG_SETTINGS_CONFFILE = '/home/apache/gdicfg/dcp/config/logging_server.conf'
DONOT_PUBLISH = False
