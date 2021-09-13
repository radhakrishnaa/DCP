from django.conf import settings as djsettings
from pprint import pprint
import logging, json
from django.http import HttpResponse

logger = logging.getLogger(__name__)

def defaultpollinginterval(request, format=None):
    logger.debug('REST GET DEFAULT_POLLING_INTERVAL')
    retdict = {'di': djsettings.DEFAULT_POLLING_INTERVAL}
    return HttpResponse(json.dumps(retdict), mimetype="application/json")

