from urllib import urlencode
from urlparse import urljoin
from django.conf import settings as djsettings
import django_cas


def _login_url_override(service):
    """Generates CAS login URL"""
    params = {'TARGET': service,'service':service,'al':1}
    if djsettings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(djsettings.CAS_EXTRA_LOGIN_PARAMS)
    return urljoin(djsettings.CAS_SERVER_URL, 'login') + '?' + urlencode(params)

# This overrides the internal _login_url method of the django_cas
# package. This is needed since django_cas passes the return URL using
# the "services" parameter, but logging into SSO with a Google account
# requires the "TARGET" parameter. The _login_url_override function is
# just like the default one in django_cas except that this one sets
# "TARGET" to the same value as "service". We cannot drop the
# "service" parameter since django_cas itself expects that to be
# present.
#
# This approach of overriding a function used internally by django_cas
# is a hack. It allows an othewise clean override of the behavior with
# minimal complexity, but we may want to investigate a more robust
# solution.
#
def override_django_cas():
  django_cas.views._login_url = _login_url_override

