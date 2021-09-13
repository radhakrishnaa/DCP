# Standard library imports
import os, json, urllib2, logging, base64, pdb, requests, re, time, datetime, copy, sys
import hashlib
import io
from pprint import pprint
import uuid

# Third-party imports
from django.conf import settings as djsettings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, StreamingHttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response
import models
import csv
import json
import ast
import re
import unicodedata
import reversion
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException, ConnectionError, HTTPError, URLRequired, TooManyRedirects
from collections import defaultdict

# Local imports
import viewshelper
from dgcs import postupload, delete as deletefromgcs

logger = logging.getLogger(__name__)

LISTUM = djsettings.LISTUM
GETUM  = djsettings.GETUM 
LISTPM = djsettings.LISTPM
GETPACKAGEBINARIES = djsettings.GETPACKAGEBINARIES
POSTPATH = djsettings.POSTPATH
DEVICEEVENTS = djsettings.DEVICEEVENTS
LISTOFELIGIBLEDEVICE = djsettings.LISTOFELIGIBLEDEVICE
TLMSLISTS = djsettings.TLMSLISTS
TLMSTARGETS = djsettings.TLMSTARGETS
TLMSMATCH = djsettings.TLMSMATCH
TLMSCHECK = djsettings.TLMSCHECK
STATS = djsettings.STATS
TIMELINE = djsettings.TIMELINE
PUBLISHEDPATH = djsettings.PUBLISHEDPATH

UPLOAD_CHUNKSIZE = djsettings.UPLOAD_CHUNKSIZE


class MD5TransparentFilter:
    """Helper class for transparently computing the MD5 checksum of a stream.
       Example usage:
            >>> iterWithMd5 = MD5TransparentFilter(file.chunks())
            >>> requests.post(HOSTNAME, data=iterWithMd5, stream=True)
            >>> print 'Computed MD5 is: %s' % iterWithMd5.hexdigest()
    """
    def __init__(self, source):
        self._sig = hashlib.md5()
        self._source = source

    def __iter__(self):
        for chunk in self._source:
            self._sig.update(chunk)
            yield chunk

    def hexdigest(self):
        return self._sig.hexdigest()


def upgradesui(request):
    template = loader.get_template(os.path.join(djsettings.SITEPATH, 'templates/ui/index.html'))
    sourcepath = os.path.join(djsettings.SITEPATH, 'static/ui/app/index.html')
    context = Context({'sourcepath': sourcepath})
    return HttpResponse(template.render(context))

def umcontroller_list(request, format=None):
    logger.debug('Request profiles from CM')
    response = requests.get(LISTUM)
    try:
        html = response.json()
    except UnicodeDecodeError, e:
        logger.info('Unable to parse REST response using guessed encoding.  Trying once more with latin-1.  Actual error:\n%s' % e)
        response.encoding = 'latin-1'
        html = response.json()
    ps = html.get('profiles')
    logger.debug('Received profiles from CM')
    retps = []
    for path in ps:
        if not filter(request, path['upgradePath']['match']):
            upstatus, created = models.UpgradePathStatus.objects.get_or_create(guid=path['guid'])
            path['upgradePath']['approval_state'] = upstatus.state
            retps.append(path)
    #logger.debug('Function: {function}, return type: {rtype}, return: {rval}'.format(function = __name__, rtype = type(retps), rval = retps))
    logger.debug('Received approval states from db')
    return HttpResponse(json.dumps(retps), mimetype="application/json")

def umcontroller_get(request, pk, format=None):
    response = requests.get(GETUM + pk)
    try:
        html = response.json()
    except UnicodeDecodeError, e:
        logger.info('Unable to parse REST response using guessed encoding.  Trying once more with latin-1.  Actual error:\n%s' % e)
        response.encoding = 'latin-1'
        html = response.json()
    if html.has_key('error') and html['error'] == 'DOES_NOT_EXIST':
        e = 'SUP with guid: {pk} does not exist -- perhaps someone deleted it?'.format(**locals())
        logger.debug(e)
        return HttpResponseBadRequest(e, mimetype="application/json", status = 404)
    ps = html.get('profile') or None
    if not ps:
        errorstring = 'I could not get the SUP for GUID: {pk}.  Please send an email to swupdate-core@motorola.com with the GUID and environment (production/staging/QA) '.format(**locals())
        logger.debug(errorstring)
        return HttpResponseBadRequest(errorstring, mimetype="application/json", status = 404)
        
    ps['guid'] = pk
    upstatus, created = models.UpgradePathStatus.objects.get_or_create(guid=pk)
    ps['next_actions'] = upstatus.next_actions()
    ps['upgradePath']['approval_state'] = upstatus.state
    try:
        # The CM/OSM backend do no keep the MD5 in their pojo, so we must grab it from the pojo stored in the SUP database 
        path = models.UpgradePath.objects.get(guid=pk)
        pathPojo = json.loads(path.pojo)
        if 'md5' in pathPojo['upgradePath']:
            ps['upgradePath']['md5'] = pathPojo['upgradePath']['md5']
    except models.UpgradePath.DoesNotExist, e:
        logger.warning("Path %s was retrieved from backend but does not exist in SUP database.. cannot display MD5")
    
    if filter(request, ps['upgradePath']['match']):
        return HttpResponseForbidden()
    else:
        return HttpResponse(json.dumps(ps), mimetype="application/json")

def um_post_next_action(request, format=None):
    logger.debug('Updating Upgrade Path State')
    params = request.POST
    action, guid, user, role, pathjson = params['action'], params['guid'], params['user'], params['role'], params['pathjson']
    publishflag = False
    pathjsondict = json.loads(pathjson)
    if (action == "PUBLISH"):
        publishflag = True
        pass
    upstatus, created = models.UpgradePathStatus.objects.get_or_create(guid=guid)
    newState = upstatus.apply_next_action(action, user, role)
    ret = {'guid' : guid, 'newState' : newState}
    if action != "CANCEL":
        _editpath(pathjsondict, publish = publishflag, action=action, newState = newState )
    return HttpResponse(json.dumps(ret), mimetype="application/json")

def um_publish_upgradePath(request, format=None):
    logger.debug('Publishing Upgrade Path')
    params = request.POST
    r = _editpath(json.loads(params['pathjson']), publish=True, action='publish', newState = 'draft')
    return HttpResponse(r, mimetype="application/json")
    
def tlmstargets(request, format=None):
    # example: in browser (logged into portal): http://127.0.0.1:8000/tlmstargets/
    params = request.GET
    logger.debug('Retrieving tlms targets')
    r = requests.get(TLMSTARGETS)
    logger.debug('Response from tlms %s' % r)
    return HttpResponse(r, mimetype="application/json")
    
def tlmslists(request, format=None):
    # example: in browser (logged into portal): http://127.0.0.1:8000/tlmslists/
    params = request.GET
    logger.debug('Retrieving tlms lists')
    r = requests.get(TLMSLISTS)
    logger.debug('Response from tlms %s' % r)
    return HttpResponse(r, mimetype="application/json")
    
def tlmsremove(request, pk, format=None):
    if not request.user.userprofile.isSuperuser():
        return HttpResponseForbidden('Must be a superuser to perform this action')
    # example: in browser (logged into portal): http://127.0.0.1:8000/tlmsremove/7ba19c18-a424-4b9e-8863-127cb8c131a4
    params = request.GET
    logger.debug('Removing a tlms list')
    r = requests.delete(TLMSLISTS + '/' + pk)
    logger.debug('Response from tlms %s' % r)
    return HttpResponse(r, mimetype="application/json")
    
def tlmsupdatetarget(request, format=None):
    if not request.user.userprofile.isSuperuser():
        return HttpResponseForbidden('Must be a superuser to perform this action')
    # for tlms target, POST is used to update, PUT is used to create...
    # POST url: http://tlms:8080/tlms-service/tlms/1/target?type=acl&softwareversion=root&user=wqpn46
    qparams = {'softwareversion': 'root', 'type': 'acl'}
    # example body
    # '"lists":["8305cdfb-3181-48ab-88c7-fefa7b616990"]}'
    logger.debug('Update the tlms target')
    r = requests.post(TLMSTARGETS, params=qparams, data=request)
    return HttpResponse(r, mimetype="application/json")

def tlmsaddlist(request, format=None):
    logger.debug('Add a tlms list')
    #r = requests.post(TLMSLISTS, data=request)
    r = requests.post(TLMSLISTS, data=request.raw_post_data)
    return HttpResponse(r, mimetype="application/json")
    
def tlmsclearlistentries(request, format=None):
    params = request.GET
    logger.info('Clear a tlms list entries')
    r = requests.delete(TLMSLISTS + '/entries/' + params['listid'], data='{entries:["all"]}')
   # r = requests.post(TLMSLISTS+'/entries/', data=request)
    return HttpResponse(r, mimetype="application/json")

def tlmsmatch(request, pk, format=None):
    # example: in browser (logged into portal): http://127.0.0.1:8000/tlmsmatch/123
    # example to tlms: http://tlms:8080/tlms-service/tlms/1/matcher/defaulter?type=acl&serialnumber=045321&softwareversion=root&user=wqpn46
    logger.debug('Match on a tlms list serial number ' + pk + ' to url ' + TLMSMATCH)
    qparams = {'serialnumber': pk, 'softwareversion': 'root', 'type': 'acl'}
    r = requests.get(TLMSMATCH, params=qparams)
    return HttpResponse(r, mimetype="application/json")

def tlmscheckeligibility(request, format=None):
    # http://tlms-qa300.blurdev.com/tlms-service/tlms/1/matcher?type=acl&serialnumber=354981050026437&softwareversion=a72a6274-8d99-4d70-9790-4c4fefe01045:1377500400000&user=wqpn46
    # Response : {"matches":true,"reason":"included","targetid":"acl.a72a6274-8d99-4d70-9790-4c4fefe01045:1377500400000"}
    logger.debug('Find device upgradabilty using tlms to url ' + TLMSCHECK)
    params = request.GET
    logger.debug('Params to tlms ... '  + str(params))
    r = requests.get(TLMSCHECK, params=params)
    return HttpResponse(r, mimetype="application/json")
    
def tlmsuploadlist(request, format=None):
    params = request.GET
    # convert the lines to json, example: sn_abc -> {"entries":["sn_abc"]}
    lines = request.body.split()
    logger.debug('Adding %s items to listid %s' % (len(lines) , params['listid']) )
    # convert the lines into upper case
    lines = [entry.upper() for entry in lines]
    # logger.debug('The list is '+ lines)
    # for index, item in enumerate(lines):
    #     logger.info('item is ' + item)
    entries = { 'entries': lines } 
    # example http://tlms:8080/tlms-service/tlms/1/list/entries/98bdda4b-6bf8-4d71-91d8-030d0c14fd07
    r = requests.post(TLMSLISTS + '/entries/' + params['listid'], data=json.dumps(entries))
    return HttpResponse(r, mimetype="application/json")

def tlmsdownloadlist(request, format=None):
    params = request.GET
    r = requests.get(TLMSLISTS + '/entries/' + params['listid'])
    html = r.json()
    lines = html.get('entries')
    info = "\n".join(lines)
    response = HttpResponse(info, mimetype="text/plain")
    response['Content-Disposition'] = 'attachment; filename="list.txt"'
    return HttpResponse(info, mimetype="text/plain")

def tlmslistsize(request, format=None):
    params = request.GET
    r = requests.get(TLMSLISTS + '/entries/' + params['listid'])
    html = r.json()
    lines = html.get('entries')
    info = {'size': len(lines)}
    return HttpResponse(json.dumps(info), mimetype="application/json")

def deviceevents(request, format=None):
    params = request.GET
    logger.debug('Retrieving device events params are %s' % params)
    r = _osm_request(params['serialnumber'])
    logger.debug('Response from osm %s' % r)
    return HttpResponse(r, mimetype="application/json")
    
def _osm_request(serialnumber, format=None):
    qparams = {'serialnumber': serialnumber}
    logger.debug('OSM request for serialnumber %s' % serialnumber)
    r = requests.get(DEVICEEVENTS, params=qparams)
    logger.debug('OSM response %s' % r)
    return r
        
def savepath(request, format=None):
    logger.debug('Saving Upgrade Path')
    params = request.POST
    r = _editpath(json.loads(params['pathjson']), publish=False, action='save', newState = 'draft')
    logger.info("Save upgrade path response = "+ repr(r))
    return HttpResponse(r, mimetype="application/json")
        
def _editpath(pathjsonasdict, publish=False, action = '', newState = '' ):
    guid = pathjsonasdict.get('guid')
    headers = {'content-type': 'application/json'}
    qparams = {'publish': publish}
    r = requests.put(POSTPATH + guid, params=qparams, data=json.dumps(pathjsonasdict), headers=headers)
    with reversion.create_revision():
        objprops = {'bvs': '%s/%s' % ( pathjsonasdict['upgradePath']['sourceVersion'], pathjsonasdict['upgradePath']['targetVersion'] ), 'pojo': json.dumps(pathjsonasdict)}
        nm, created = models.UpgradePath.objects.get_or_create(guid=guid, defaults=objprops)
        if not created: # Already exists, need to update the fields
            for key, value in objprops.iteritems():
                setattr(nm, key, value)
                nm.save()
                continue
            pass
        pass
        reversion.set_comment("UI/action=%s/newstate=%s/publish=%s" % ( action, newState, publish ))
    return r

def filter(request, matchdict):
    prof = request.user.userprofile
    
    # We need to apply all filters so user can't see something he/she doesn't have access to
    # Example row in upgrade path:
    """
    {u'upgradePath': {u'defaultUrl': {u'encrypted': False, u'baseUrl': u'http://cdn.google.com/motorola/downloads/'}, u'controls': [{u'startDate': 1369149791851, u'timeSlots': [{u'duration': 120, u'start': 600}], u'allowTargetedLists': False, u'dailyDownloads': 2, u'requestTypesAllowed': [u'USER'], u'numDays': 3}], u'sourceVersion': u'Blur_Version.99.22.7.XT901.USC.en.US', u'state': u'STOPPED', u'packageId': u'c5585d81-466b-4de8-ad7b-04e24d5256cc', u'targetVersion': u'Blur_Version.99.22.13.XT901.USC.en.US', u'match': {u'hwType': u'XT902', u'carrier': u'USC', u'region': u'BR', u'language': u'en'}}, u'guid': u'24a61069-8baa-46da-8cad-1070fe09af28', u'metaData': {u'annoy': u'30,60,180', u'forced': True, u'postInstallNotes': u'', u'downloadOptionsNotes': u'MotorolaSoftwareUpdate', u'flavour': u'MotorolaSoftwareUpdate', u'installTime': 10, u'releaseNotes': u'https://motorola-global-portal.custhelp.com/app/answers/detail/a_id/93412', u'trackingId': u'CANNOTTRACKTHIS', u'wifionly': True, u'reportingTag': u'NOREPORTINGTAG', u'upgradeNotification': u'', u'version': u'Blur_Version.98.22.13.XT901.USC.en.US', u'metaVersion': 1, u'preInstallNotes': u'', u'minVersion': u'Blur_Version.98.22.7.XT901.USC.en.US', u'extraSpace': 0, u'size': 5479242, u'showPreDownloadDialog': True, u'showDownloadOptions': False, u'preDownloadNotificationExpiryMins': 1440, u'preInstallNotificationExpiryMins': 1440}}
    """
    # Example row in packages:
    """
    {"region":"US","hwType":"ghost_tmo","packageid":"ff3e029c-f0fb-4361-b93e-4a66936d50ad","source":"Blur_Version.139.1.21.ghost_tmo.T-Mobile.en.US","name":"Blur_Version.139.1.21-139.1.24.ghost_tmo.T-Mobile.en.US","carrier":"T-Mobile","language":"en"}
    """
    # If the profile has products but the current path's product match is not in the profile, filter
    if prof.get_products() and matchdict['product'] not in prof.get_products():
        #logger.info('Row filtered out because the logged in user [{user}s] can only see [{products}s], while the path match is for product [{product}s]'.format(
        #    user = request.user.username, products = prof.get_products(), product = matchdict['product']))
        return True
    
    if prof.get_carriers() and matchdict['carrier'] not in prof.get_carriers():
        #logger.info('Row filtered out because the logged in user [{user}s] can only see [{carriers}s], while the path match is for carrier [{carrier}s]'.format(
        #    user = request.user.username, carriers = prof.get_carriers(), carrier = matchdict['carrier']))
        return True
    
    if prof.get_regions() and matchdict['region'] not in prof.get_regions():
        #logger.info('Row filtered out because the logged in user [{user}s] can only see [{regions}s], while the path match is for region [{region}s]'.format(
        #    user = request.user.username, regions = prof.get_regions(), region = matchdict['region']))
        return True

def getCurrentUser(request, format=None):
    # Auto-populate the UserProfile table (role-based access) for user if logged in for the first time; since this model is linked to User model 
    # by 1:1 relation in Django, it is magically accessible as request.user.userprofile
    userprof, created = models.UserProfile.objects.get_or_create(user=request.user)
    if created:
        logger.debug('Creating role-based access profile for user %s (first time logging in)' % userprof)
        pass
    ret = request.user.userprofile.to_hash()
    logger.debug('Function: {function}, return type: {rtype}, return: {rval}'.format(function = __name__, rtype = type(ret), rval = ret))
    return HttpResponse(json.dumps(ret), mimetype="application/json")


def uploadtogcs(filename, someiter):
    iterWithMd5 = MD5TransparentFilter(someiter)
    try:
        logger.debug('Starting to upload binary GCS.. objectname is %s' % GETPACKAGEBINARIES)
        pkgresp = postupload(filename, iterWithMd5)
        logger.info('Computed MD5 is: %s' % iterWithMd5.hexdigest())
        j = pkgresp.json()
        j['md5'] = iterWithMd5.hexdigest()
        pkgresp._content = json.dumps(j)  # insert MD5 into response content (hack)
        logger.debug('Finished uploading binary: ' + pkgresp.text)
    except:
        print 'Error in uploading to GCS ...'
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
        raise Exception("Unexpected error:", sys.exc_info()[0])

    if pkgresp.status_code != 200:
        raise Exception( 'Uploading package to GCS failed with return code: %d' % pkgresp.status_code )
    return pkgresp


def _pkgtopm(someiter):
    iterWithMd5 = MD5TransparentFilter(someiter)
    try:
        logger.debug('Starting to upload binary to: %s' % GETPACKAGEBINARIES)
        pkgresp = requests.post(GETPACKAGEBINARIES, data=iterWithMd5, stream=True)
        logger.info('Computed MD5 is: %s' % iterWithMd5.hexdigest())
        j = pkgresp.json()
        j['md5'] = iterWithMd5.hexdigest()
        pkgresp._content = json.dumps(j)  # insert MD5 into response content (hack)
        logger.debug('Finished uploading binary: ' + pkgresp.text)
    except ConnectionError:
        raise Exception('requests.exceptions.ConnectionError connecting to package management server.  This is recoverable, please retry at a later time.')
    except URLRequired:
        raise Exception('requests.exceptions.URLRequired: Invalid Package Management URL %s.  Correct the settings file used by Django by pointing to valid one' % GETPACKAGEBINARIES)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
        raise Exception("Unexpected error:", sys.exc_info()[0])

    if pkgresp.status_code != 200:
        raise Exception( 'Uploading package to Package management server failed with return code: %d' % pkgresp.status_code )
    if pkgresp.json().get('size') == 0:
        raise Exception( 'Either supplied package is empty (0 bytes) or package management server failed to store it.' )

    return pkgresp
    
def uploadbinary(request, format=None):
    #logger.debug('Received request to upload binary: %s' % request)
    binary = request.FILES['binary']
    # IMPORTANT NOTE:
    # Please uplaod the binary file to GCS/PM FIRST before creating SUP in CM
    usecds = request.GET.get('usecds', 'true') == 'true'
        
    try:
      	# Figure out which repository is chosen
        if usecds:
            logger.debug('Uploading binary to GCS')
            # make a random UUID
            s = uuid.uuid4()
            newguid = s.urn.split(':')[-1]
            gsobjectname = '%s.%s' % (binary.name, newguid)
            resp = uploadtogcs(gsobjectname, binary.chunks())
            respJson = resp.json()
            packageguid, packagesize, packagemd5 = respJson.get('name'), int(respJson.get('size')), respJson.get('md5')
        else:
            logger.debug('Uploading binary to PM')
            resp = _pkgtopm(binary.chunks())
            respJson = resp.json()
            packageguid, packagesize, packagemd5 = respJson.get('packageid'), int(respJson.get('size')), respJson.get('md5')
    except Exception, e:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
        return HttpResponseBadRequest(str(e))
    
    newpathdict = copy.deepcopy(viewshelper.NEW_PATH_DICT)
    newpathdict = viewshelper._populate_local_pojo_dict(newpathdict, 'file:///{}'.format(binary.name), packageguid, packagesize, packagemd5, request, 'GCS' if usecds else 'PM')
    if logger.isEnabledFor(logging.DEBUG):
        pprint(newpathdict)

    headers = {'content-type': 'application/json'}
    jsondata = json.dumps(newpathdict)
    try:
        upathresp = requests.post(POSTPATH, data=jsondata, headers=headers)
    except ConnectionError:
        return HttpResponseBadRequest( 'Error connecting to Upgrade Path server at %s.  This is recoverable, please retry at a later time.' % POSTPATH )
    except URLRequired:
        return HttpResponseBadRequest('Invalid Upgrade Path Server URL %s.  This is a misconfiguration in django settings module' % POSTPATH)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest( 'Unexpected error: ', sys.exc_info()[0])

    if upathresp.status_code == 409:
        return HttpResponseBadRequest( 'This SUP [{b}] already exists.'.format(b=newpathdict['upgradePath']['sourceVersion']) )

    if upathresp.status_code != 200:
        return HttpResponseBadRequest( 'Upgrade Path server returned status code: %d during creation of the upgrade path' % upathresp.status_code )
        
    newpathguid = upathresp.json().get('guid')
    respdict = {'guid': newpathguid}
    try:
        models.UpgradePathStatus.objects.create(guid=newpathguid)
    except:
        logger.debug('Failed to create a status object in Django DB for the upgrade path [{newpathguid}].  No worries, we will create it on next read'.format(**locals()))
        pass
    with reversion.create_revision():
        objprops = {'bvs': '%s/%s' % ( newpathdict['upgradePath']['sourceVersion'], newpathdict['upgradePath']['targetVersion'] ), 
            'pojo': jsondata}
        nm, created = models.UpgradePath.objects.get_or_create(guid=newpathguid, defaults=objprops)
        if not created: # Already exists, need to update the fields
            for key, value in objprops.iteritems():
                setattr(nm, key, value)
                nm.save()
                continue
            pass
        pass
        reversion.set_comment("/uploadbinary/publish=false")
    return HttpResponse(json.dumps(respdict), mimetype="application/json")


def getVersion(request, format=None):
    logger.debug('Reading version file from local file system')
    logger.debug(djsettings.SITEPATH)
    versionFile = djsettings.SITEPATH + '/static/version'
    logger.debug(versionFile)
    with open(versionFile, 'r') as f:
        var = f.read()
        logger.debug('version string is %s ' %var )
    return HttpResponse(var)

def autojenkins(request, format=None):
    """
    from django_cas.backends import CASBackend
    casbackendinst = CASBackend()
    print 'Getting auth header if available'
    authheader = request.META.get('HTTP_AUTHORIZATION')
    print 'authheader=%s' % authheader
    authtype, ticket = authheader.split()
    print 'authtype=%s, ticket=%s' % (authtype, ticket)
    if authtype == 'ticket':
        user = casbackendinst.authenticate_CAS_2_SAML_1_0(ticket, '/getpackagefromjenkins/', request)
        pass
    pass
    if not user:
        return HttpResponseForbidden()

    respdict = {'guid': 'auth'}
    return HttpResponse(json.dumps(respdict), mimetype="application/json")
    """
    
    params = request.POST
    requiredparams = set(('zipFileUrl', 'userName', 'apitoken'))
    suppliedparams = set(params)
    missingparams = requiredparams - suppliedparams
    if missingparams:
        return HttpResponseBadRequest( 'Missing mandatory parameters, %s' % (missingparams,) )
    zipFileUrl, username, apitoken = params['zipFileUrl'].strip(), params['userName'].strip(), base64.b64decode(params['apitoken'].strip()).strip()
    if None in (zipFileUrl, username, apitoken):
        return HttpResponseBadRequest( 'Missing post parameters, namely: zipFileUrl=%s, username=%s, apitoken=%s' % (zipFileUrl, username, apitoken) )

    allowpolling = bool(params.get('allowpolling', False))
    allowuser = bool(params.get('allowuser', False))
    allowsetup = bool(params.get('allowsetup', False))
    usecds = bool(params.get('usecds', False))

    viplists = params.get('lists', '')
    # Iterate over the list labels to find list ids
    # No list id, this request can't be fulfilled
    viplistguids = set()
    for listlabelraw in viplists.split(','):
        listlabel = listlabelraw.strip()
        if not listlabel:
            continue
        try:
            params = {'label': listlabel}
            listresp = requests.get(TLMSLISTS, params=params)
        except ConnectionError:
            return HttpResponseBadRequest('Error connecting to TLMS server.  This is recoverable, please retry at a later time.')
        except URLRequired:
            return HttpResponseBadRequest('Invalid URL %s.  Please reenter a correct one and retry.' % TLMSLISTS)
        except:
            if logger.isEnabledFor(logging.DEBUG):
                pprint(sys.exc_info())
                pass
            return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])
        
        if listresp.status_code != 200:
            return HttpResponseBadRequest( 'Obtaining GUID using the list label failed with status code: %d.  For security, I won\'t create this SUP' % listresp.status_code )
        listjson = json.loads(listresp.text)
        # If we received multiple lists as a response for that same label, again, don't create this upgrade path
        if len(listjson['lists']) != 1:
            return HttpResponseBadRequest( 'Given a label, I should only find one list.  Found either none on more than 1. [%s]' % listjson )
        viplistguids.add(listjson['lists'][0]['listid'])
        continue
    
    try:
        zipFileUrl, zipfilename, xmlFileUrl, md5FileUrl = viewshelper._parse_zipfile_url(zipFileUrl)
    except:
        return HttpResponseBadRequest('Supplied ZIP file name for the delta package is wrong')

    auth = HTTPBasicAuth(username, apitoken)
    try:
        rzip = requests.get(zipFileUrl, auth=auth, stream=True)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to Jenkins server.  This is recoverable, please retry at a later time.')
    except URLRequired:
        return HttpResponseBadRequest('Invalid Zip File URL %s.  Please reenter a correct one and retry.' % zipFileUrl)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])
        
    if rzip.status_code != 200:
        return HttpResponseBadRequest( 'Unable to stream package binary from Jenkins because request to get the file returned in status code: %d' % rzip.status_code )

    try:
        # Figure out which repository is chosen
        if usecds:
            logger.debug('Uploading binary to GCS')
            # make a random UUID
            s = uuid.uuid4()
            newguid = s.urn.split(':')[-1]
            gsobjectname = '%s.%s' % (zipfilename, newguid)
            resp = uploadtogcs(gsobjectname, rzip.iter_content(chunk_size=UPLOAD_CHUNKSIZE))
            respJson = resp.json()
            packageguid, packagesize, packagemd5 = respJson.get('name'), int(respJson.get('size')), respJson.get('md5')
        else:
            logger.debug('Uploading binary to PM')
            resp = _pkgtopm(rzip.iter_content(chunk_size=UPLOAD_CHUNKSIZE))
            respJson = resp.json()
            packageguid, packagesize, packagemd5 = respJson.get('packageid'), int(respJson.get('size')), respJson.get('md5')
    except Exception, e:
        return HttpResponseBadRequest(str(e))

    try:
        xmldoc = requests.get(xmlFileUrl, auth=auth)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to Jenkins server.  This is recoverable, please retry at a later time.')
    except URLRequired:
        return HttpResponseBadRequest('Invalid XML File URL %s.  Please reenter a correct one and retry.' % xmlFileUrl)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])
        
    if xmldoc.status_code != 200:
        return HttpResponseBadRequest( 'Unable to parse XML because request to get the XML file returned in status code: %d' % xmldoc.status_code )


    newpathdict = copy.deepcopy(viewshelper.AUTOJENKINS_PATH_DICT)
    newpathdict = viewshelper._populate_pojo_dict(newpathdict, zipFileUrl, xmlFileUrl, xmldoc.text, packageguid, packagesize, packagemd5, 'GCS' if usecds else 'PM')
    newpathdict = viewshelper._populate_autopath_dict(newpathdict, ','.join(viplistguids) if len(viplistguids) else None, allowpolling, allowuser, allowsetup)
    if logger.isEnabledFor(logging.DEBUG):
        pprint(newpathdict)
        pass

    headers = {'content-type': 'application/json'}
    jsondata = json.dumps(newpathdict)
    qparams = {'publish': True}

    try:
        upathresp = requests.post(POSTPATH, params=qparams, data=jsondata, headers=headers)
    except ConnectionError:
        return HttpResponseBadRequest( 'Error connecting to Upgrade Path server at %s.  This is recoverable, please retry at a later time.' % POSTPATH )
    except URLRequired:
        return HttpResponseBadRequest('Invalid Upgrade Path Server URL %s.  This is a misconfiguration in django settings module' % POSTPATH)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest( 'Unexpected error: ', sys.exc_info()[0])

    if upathresp.status_code == 409:
        return HttpResponseBadRequest( 'This SUP already exists.' )

    if upathresp.status_code != 200:
        return HttpResponseBadRequest( 'Upgrade Path server returned status code: %d during creation of the upgrade path' % upathresp.status_code )
        
    newpathguid = upathresp.json().get('guid')
    respdict = {'guid': newpathguid}
    try:
        models.UpgradePathStatus.objects.create(guid=newpathguid)
    except:
        logger.debug('Failed to create a status object in Django DB for the upgrade path [{newpathguid}].  No worries, we will create it on next read'.format(**locals()))
        pass
    with reversion.create_revision():
        objprops = {'bvs': '%s/%s' % ( newpathdict['upgradePath']['sourceVersion'], newpathdict['upgradePath']['targetVersion'] ), 'pojo': jsondata}
        nm, created = models.UpgradePath.objects.get_or_create(guid=newpathguid, defaults=objprops)
        if not created: # Already exists, need to update the fields
            for key, value in objprops.iteritems():
                setattr(nm, key, value)
                nm.save()
                continue
            pass
        pass
        reversion.set_comment("/autojenkins/publish=true")
    return HttpResponse( json.dumps(respdict), mimetype="application/json")

def getxmlfromjenkins(request, format=None):
    params = request.POST
    zipFileUrl, username, apitoken, usecds = params['zipFileUrl'].strip(), params['userName'].strip(), base64.b64decode(params['apitoken'].strip()).strip(), params.get('usecds', 'false') == 'true'
    try:
        zipFileUrl, zipfilename, xmlFileUrl, md5FileUrl = viewshelper._parse_zipfile_url(zipFileUrl)
    except:
        return HttpResponseBadRequest('Supplied ZIP file name for the delta package (or reverse delta package) is wrong')

    auth = HTTPBasicAuth(username, apitoken)

    try:
        xmldoc = requests.get(xmlFileUrl, auth=auth, verify=False)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to Jenkins server.  This is recoverable, please retry at a later time.')
    except URLRequired:
        return HttpResponseBadRequest('Invalid XML File URL %s.  Please reenter a correct one and retry.' % xmlFileUrl)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])
        
    if xmldoc.status_code != 200:
        return HttpResponseBadRequest( 'Unable to parse XML because request to get the XML file returned in status code: %d' % xmldoc.status_code )
   
    newpathdict = copy.deepcopy(viewshelper.NEW_XMLPATH_DICT)
    print "before pojodict: "
    newpathdict = viewshelper._populate_XMLpojo_dict(newpathdict, xmlFileUrl, xmldoc.text)
    jsondata = json.dumps(newpathdict)
    return HttpResponse(jsondata)
    

def getpackagefromjenkins(request, format=None):
    params = request.POST
    zipFileUrl, username, apitoken, usecds = params['zipFileUrl'].strip(), params['userName'].strip(), base64.b64decode(params['apitoken'].strip()).strip(), params.get('usecds', 'false') == 'true'
    try:
        zipFileUrl, zipfilename, xmlFileUrl, md5FileUrl = viewshelper._parse_zipfile_url(zipFileUrl)
    except:
        return HttpResponseBadRequest('Supplied ZIP file name for the delta package (or reverse delta package) is wrong')

    auth = HTTPBasicAuth(username, apitoken)
    try:
        rzip = requests.get(zipFileUrl, auth=auth, stream=True, verify=False)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to Jenkins server.  This is recoverable, please retry at a later time.')
    except URLRequired:
        return HttpResponseBadRequest('Invalid Zip File URL %s.  Please reenter a correct one and retry.' % zipFileUrl)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])
        
    if rzip.status_code != 200:
        return HttpResponseBadRequest( 'Unable to stream package binary from Jenkins because request to get the file returned in status code: %d' % rzip.status_code )

    try:
        md5sresponse = requests.get(md5FileUrl, auth=auth)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to Jenkins server.  This is recoverable, please retry at a later time.')
    except URLRequired:
        return HttpResponseBadRequest('Invalid MD5 URL %s.  Please log this bug in Jira as syntax for looking up MD5 file has changed and requires update to portal UI code' % md5FileUrl)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])

    md5 = ''
    if md5sresponse.status_code == 200:
        md5s = md5sresponse.text.split()
        for index, item in enumerate(md5s):
            if item.endswith(zipfilename):
                md5 = md5s[index - 1]
                break
            pass
        logger.info('MD5 for the file: ' + md5)
        pass
    else:
        logger.warn( 'Unable to parse MD5 because request to get the MD5 file returned in status code: %d' % md5sresponse.status_code )
    

    try:
        # Figure out which repository is chosen
        if usecds:
            logger.debug('Uploading binary to GCS')
            # make a random UUID
            s = uuid.uuid4()
            newguid = s.urn.split(':')[-1]
            gsobjectname = '%s.%s' % (zipfilename, newguid)
            resp = uploadtogcs(gsobjectname, rzip.iter_content(chunk_size=UPLOAD_CHUNKSIZE))
            respJson = resp.json()
            packageguid, packagesize, packagemd5 = respJson.get('name'), int(respJson.get('size')), respJson.get('md5')
        else:
            logger.debug('Uploading binary to PM')
            resp = _pkgtopm(rzip.iter_content(chunk_size=UPLOAD_CHUNKSIZE))
            respJson = resp.json()
            packageguid, packagesize, packagemd5 = respJson.get('packageid'), int(respJson.get('size')), respJson.get('md5')
    except Exception, e:
        return HttpResponseBadRequest(str(e))

    try:
        xmldoc = requests.get(xmlFileUrl, auth=auth)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to Jenkins server.  This is recoverable, please retry at a later time.')
    except URLRequired:
        return HttpResponseBadRequest('Invalid XML File URL %s.  Please reenter a correct one and retry.' % xmlFileUrl)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])
        
    if xmldoc.status_code != 200:
        return HttpResponseBadRequest( 'Unable to parse XML because request to get the XML file returned in status code: %d' % xmldoc.status_code )
    
    newpathdict = copy.deepcopy(viewshelper.NEW_PATH_DICT)
    newpathdict = viewshelper._populate_pojo_dict(newpathdict, zipFileUrl, xmlFileUrl, xmldoc.text, packageguid, packagesize, packagemd5, 'GCS' if usecds else 'PM')
    if logger.isEnabledFor(logging.DEBUG):
        pprint(newpathdict)
        pass

    headers = {'content-type': 'application/json'}
    jsondata = json.dumps(newpathdict)
    try:
        upathresp = requests.post(POSTPATH, data=jsondata, headers=headers)
    except ConnectionError:
        return HttpResponseBadRequest( 'Error connecting to Upgrade Path server at %s.  This is recoverable, please retry at a later time.' % POSTPATH )
    except URLRequired:
        return HttpResponseBadRequest('Invalid Upgrade Path Server URL %s.  This is a misconfiguration in django settings module' % POSTPATH)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest( 'Unexpected error: ', sys.exc_info()[0])

    if upathresp.status_code == 409:
        return HttpResponseBadRequest( 'This SUP already exists.' )

    if upathresp.status_code != 200:
        return HttpResponseBadRequest( 'Upgrade Path server returned status code: %d during creation of the upgrade path' % upathresp.status_code )
        
    newpathguid = upathresp.json().get('guid')
    respdict = {'guid': newpathguid}
    try:
        models.UpgradePathStatus.objects.create(guid=newpathguid)
    except:
        logger.debug('Failed to create a status object in Django DB for the upgrade path [{newpathguid}].  No worries, we will create it on next read'.format(**locals()))
        pass
    with reversion.create_revision():
        objprops = {'bvs': '%s/%s' % ( newpathdict['upgradePath']['sourceVersion'], newpathdict['upgradePath']['targetVersion'] ), 'pojo': jsondata}
        nm, created = models.UpgradePath.objects.get_or_create(guid=newpathguid, defaults=objprops)
        if not created: # Already exists, need to update the fields
            for key, value in objprops.iteritems():
                setattr(nm, key, value)
                nm.save()
                continue
            pass
        pass
        reversion.set_comment("/getpackagefromjenkins/publish=false")
    return HttpResponse(json.dumps(respdict), mimetype="application/json")
    
def getpackagewithoutxmlfromjenkins(request, format=None):
    logger.debug('Downloading binary from  jenkins')
    params = request.POST
    zipFileUrl, username, apitoken, usecds = params['zipFileUrl'].strip(), params['userName'].strip(), base64.b64decode(params['apitoken'].strip()).strip(), params.get('usecds', 'false') == 'true'
    try:
        zipFileUrl, zipfilename, xmlFileUrl, md5FileUrl = viewshelper._parse_zipfile_url(zipFileUrl)
    except:
        return HttpResponseBadRequest('Supplied ZIP file name for the delta package (or reverse delta package) is wrong')

    auth = HTTPBasicAuth(username, apitoken)
    try:
        rzip = requests.get(zipFileUrl, auth=auth, stream=True, verify=False)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to Jenkins server while getting zip file.  This is recoverable, please retry at a later time.')
    except URLRequired:
        return HttpResponseBadRequest('Invalid Zip File URL %s.  Please reenter a correct one and retry.' % zipFileUrl)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error while getting zip file:", sys.exc_info()[0])
        
    if rzip.status_code != 200:
        return HttpResponseBadRequest( 'Unable to stream package binary from Jenkins because request to get the file returned in status code: %d' % rzip.status_code )

    try:
        md5sresponse = requests.get(md5FileUrl, auth=auth, verify=False)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to Jenkins server while getting md5.  This is recoverable, please retry at a later time.')
    except URLRequired:
        return HttpResponseBadRequest('Invalid MD5 URL %s.  Please log this bug in Jira as syntax for looking up MD5 file has changed and requires update to portal UI code' % md5FileUrl)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])

    md5 = ''
    if md5sresponse.status_code == 200:
        md5s = md5sresponse.text.split()
        for index, item in enumerate(md5s):
            if item.endswith(zipfilename):
                md5 = md5s[index - 1]
                break
            pass
        logger.info('MD5 for the file: ' + md5)
        pass
    else:
        logger.warn( 'Unable to parse MD5 because request to get the MD5 file returned in status code: %d' % md5sresponse.status_code )

    try:
        # Figure out which repository is chosen
        if usecds:
            print 'Uploading binary to GCS'
            logger.debug('Uploading binary to GCS')
            # make a random UUID
            s = uuid.uuid4()
            newguid = s.urn.split(':')[-1]
            gsobjectname = '%s.%s' % (zipfilename, newguid)
            resp = uploadtogcs(gsobjectname, rzip.iter_content(chunk_size=UPLOAD_CHUNKSIZE))
            respJson = resp.json()
            packageguid, packagesize, packagemd5 = respJson.get('name'), int(respJson.get('size')), respJson.get('md5')
        else:
            logger.debug('Uploading binary to PM')
            resp = _pkgtopm(rzip.iter_content(chunk_size=UPLOAD_CHUNKSIZE))
            respJson = resp.json()
            packageguid, packagesize, packagemd5 = respJson.get('packageid'), int(respJson.get('size')), respJson.get('md5')
    except Exception, e:
        return HttpResponseBadRequest(str(e))

    newpathdict = copy.deepcopy(viewshelper.NEW_PATH_DICT)
    newpathdict = viewshelper._populate_pojo_dict_noxml(newpathdict, zipFileUrl, request, packageguid, packagesize, packagemd5, 'GCS' if usecds else 'PM')
    
    if logger.isEnabledFor(logging.DEBUG):
        pprint(newpathdict)
        pass

    headers = {'content-type': 'application/json'}
    jsondata = json.dumps(newpathdict)
    try:
        upathresp = requests.post(POSTPATH, data=jsondata, headers=headers)
    except ConnectionError:
        return HttpResponseBadRequest( 'Error connecting to Upgrade Path server at %s.  This is recoverable, please retry at a later time.' % POSTPATH )
    except URLRequired:
        return HttpResponseBadRequest('Invalid Upgrade Path Server URL %s.  This is a misconfiguration in django settings module' % POSTPATH)
    except:
        print 'Unexpected error while creating path'
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest( 'Unexpected error while creating path : ', sys.exc_info()[0])

    if upathresp.status_code == 409:
        return HttpResponseBadRequest( 'This SUP already exists.' )

    if upathresp.status_code != 200:
        return HttpResponseBadRequest( 'Upgrade Path server returned status code: %d during creation of the upgrade path' % upathresp.status_code )
        
    newpathguid = upathresp.json().get('guid')
    respdict = {'guid': newpathguid}
    try:
        models.UpgradePathStatus.objects.create(guid=newpathguid)
    except:
        logger.debug('Failed to create a status object in Django DB for the upgrade path [{newpathguid}].  No worries, we will create it on next read'.format(**locals()))
        pass
    with reversion.create_revision():
        objprops = {'bvs': '%s/%s' % ( newpathdict['upgradePath']['sourceVersion'], newpathdict['upgradePath']['targetVersion'] ), 'pojo': jsondata}
        nm, created = models.UpgradePath.objects.get_or_create(guid=newpathguid, defaults=objprops)
        if not created: # Already exists, need to update the fields
            for key, value in objprops.iteritems():
                setattr(nm, key, value)
                nm.save()
                continue
            pass
        pass
        reversion.set_comment("/getpackagefromjenkins/publish=false")
    return HttpResponse(json.dumps(respdict), mimetype="application/json")

def deletepathandpackage(request, format=None):
    logger.debug("In deletepathandpackage ...")
    params = request.POST
    pathguid, packageguid, packagestore = params['pathguid'], params['packageguid'], params.get('packagestore', 'PM')
    logger.debug("Received POST parameters for the request.  pathguid={pathguid}, packageguid={packageguid}, packagestore={packagestore}".format(**locals()))

    # Delete path first
    logger.debug("Deleting a path, using: %s" % (GETUM + pathguid))
    try:
        delresp = requests.delete(GETUM + pathguid)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to upgrade path back-end server at %s.  This is recoverable, please retry at a later time.' % GETUM)
    except URLRequired:
        return HttpResponseBadRequest('Invalid upgrade path URL %s.  Please reenter a correct one and retry.' % (GETUM + params['guid']))
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])

    if delresp.status_code != 200:
        return HttpResponse(status = delresp.status_code)

    # Delete the package next
    try:
        # Figure out which repository is chosen
        if packagestore == 'GCS':
            logger.debug("Deleting the package from GCS")
            deletefromgcs(packageguid)
        elif packagestore == 'PM':
            logger.debug("Deleting the package, using: %s" % (GETPACKAGEBINARIES + '/' + packageguid))
            delresp = requests.delete(GETPACKAGEBINARIES + '/' + packageguid)
        else:
            return HttpResponseBadRequest('Can\'t delete package binary because unknown package store {packagestore}.  Please delete {packageguid} manually.'.format(**locals()))
    except Exception, e:
        return HttpResponseBadRequest(str(e))

    with reversion.create_revision():
        try:
            path = models.UpgradePath.objects.get(guid=pathguid)
            # -- Keep the entry in the local SUP database.. until we decide to change our retention policy
            #path.delete()
            reversion.set_comment("/deletepathandpackage")
        except models.UpgradePath.DoesNotExist, e:
            logger.warning("Path %s does not exist in SUP database.. skipping this step of deletepathandpackage") 
    
    return HttpResponse(status = 200)

def stats(request, pk, format=None):
    logger.debug("In stats, with GUID: " + pk)
    try:
        url = '%s/?guid=%s' % (STATS, pk)
        statsresp = requests.get(url)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to stats back-end server at %s.  This is recoverable, please retry at a later time.' % STATS)
    except URLRequired:
        return HttpResponseBadRequest('Invalid stats URL %s.  Please reenter a correct one and retry.' % url)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])

    if statsresp.status_code != 200:
        return HttpResponse(status = statsresp.status_code)

    # We retrieved stats for a single SUP.  Let us create a dict with stats to be displayed
    '''
+-------------------------+-------------------------+-------------------------+
|Check type               |#devices checked         |#devices allowed         |
+-------------------------+-------------------------+-------------------------+
|User                     |                         |                         |
+-------------------------+-------------------------+-------------------------+
|Polling                  |                         |                         |
+-------------------------+-------------------------+-------------------------+
|Setup                    |                         |                         |
+-------------------------+-------------------------+-------------------------+
|Notified                 |                         |                         |
+-------------------------+-------------------------+-------------------------+
|Other                    |                         |                         |
+-------------------------+-------------------------+-------------------------+
|Total                    |                         |                         |
+-------------------------+-------------------------+-------------------------+
'''
    try:
        retstats = json.loads(statsresp.text)
    except ValueError:
        logger.debug('I could not parse the stats for the SUP {pk}.  Most likely, this is a new SUP with no stats.  Ignoring. '.format(**locals()))
        return HttpResponse('', mimetype="application/json")
    
    curpathstats = defaultdict(lambda: 0)
    curpathstats.update(retstats)

    checktypestats = {}
    checktypestats['user'] = {'checked': curpathstats['_system.CHECK.user'], 'eligible': curpathstats['user.ELIGIBLE_NOW']}
    checktypestats['polling'] = {'checked': curpathstats['_system.CHECK.polling'], 'eligible': curpathstats['polling.ELIGIBLE_NOW']}
    checktypestats['setup'] = {'checked': curpathstats['_system.CHECK.setup'], 'eligible': curpathstats['setup.ELIGIBLE_NOW']}
    checktypestats['notification'] = {'checked': curpathstats['_system.CHECK.notification'], 'eligible': curpathstats['notification.ELIGIBLE_NOW']}
    checktypestats['other'] = {'checked': curpathstats['_system.CHECK.other'], 'eligible': curpathstats['other.ELIGIBLE_NOW']}
    checktypestats['total'] = {'checked': sum(curpathstats[key] for key in ('_system.CHECK.user','_system.CHECK.polling','_system.CHECK.setup','_system.CHECK.notification','_system.CHECK.other',)),
                               'eligible': curpathstats['_system.CHECK.ELIGIBLE_NOW']}

    curpathstats.update(checktypestats)
    return HttpResponse(json.dumps(curpathstats), mimetype="application/json")

def publishedpath(request, pk, format=None):
    logger.debug("In publishedpath, with GUID: " + pk)
    try:
        url = '%s/%s' % (PUBLISHEDPATH, pk)
        ppathresp = requests.get(url)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to OSM back-end server at %s.  This is recoverable, please retry at a later time.' % PUBLISHEDPATH)
    except URLRequired:
        return HttpResponseBadRequest('Invalid OSM URL %s.  Please reenter a correct one and retry.' % url)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])

    if ppathresp.status_code != 200:
        return HttpResponse(status = ppathresp.status_code)

    return HttpResponse(ppathresp.text, mimetype="application/json")
    
class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value
         
def getdeviceeligibleforupgrade(request,  format=None):
   
    guid=request.GET['guid']
    #guid = 'c902986e-04b5-46f8-982e-dbb3717f905f'
    state=request.GET['state']
    batchsize= str(djsettings.BATCH_SIZE);
    logger.debug("state: " + str(state))
    logger.debug("batchsize: " + str(batchsize))
    type="";
    
    for key in request.GET:
        if key == "type":
            type=request.GET[key]
            logger.debug("type in request: " +str(type));
    
    try:
        if type == "":
            res = requests.get(LISTOFELIGIBLEDEVICE + '/guid/' + request.GET['guid'] + '/state/' + request.GET['state'] + '?batch='+batchsize)
            #res = requests.get(LISTOFELIGIBLEDEVICE + '/guid/' + guid + '/state/' + request.GET['state'] + '?batch='+batchsize)
        else:
            res = requests.get(LISTOFELIGIBLEDEVICE + '/guid/' + request.GET['guid'] + '/state/' + request.GET['state'] + '?batch='+batchsize+'&type='+type)
            #res = requests.get(LISTOFELIGIBLEDEVICE + '/guid/' + guid + '/state/' + request.GET['state'] + '?batch='+batchsize+'&type='+type)
         
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to OSM back-end server at %s.  This is recoverable, please retry at a later time.' % LISTOFELIGIBLEDEVICE)
    except URLRequired:
        return HttpResponseBadRequest('Invalid OSM URL %s.  Please reenter a correct one and retry.' % url)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])

    if res.status_code != 200:
        return HttpResponse(status = res.status_code)
    global rows
    
    if((res.json())==[]):
        return HttpResponse(res, mimetype="application/json")
    
    rows=DATA2CSV((res).json())
    
    
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    return HttpResponse(response)
	
def DATA2CSV(res):
    strArray=['SerialNumber','deviceid','IMEI','IMEI2','IMSI','IMSI2','hwType','carrier','region','android.model','android.carrier',
                    'provisionedTime','softwareVersion','time','state','clientStatus','src','dest','Notified','RequestPermission','GettingDescriptor','GettingPackage','Querying','Upgrading',
                    'Result_DONE','Result_FAILED','reportingTag','trackingId','metaDataVersion','info','deviceInfo'];
    finalVal = []
    count = 0
    finalVal.append(strArray)  
    for x in range(0, len(res)):
        batch = res[x]
        for guid in batch:
            csvrow = {}
            devstats = batch[guid]
            data = json.loads(json.dumps(devstats))
            for key, value in data.items():
                if key.find(guid) > -1:
                    try:
                        substats = str(data[key])
                        datainner =json.loads(substats)
                        for key1, value1 in datainner.items():
                            if key1 == "deviceInfo" :
                                csvrow['deviceInfo'] =value1;
                                datadeviceinfo =json.loads(json.dumps(value1))
                                for key2, value2 in datadeviceinfo.items():
                                    csvrow[key2] = value2
                            elif key1 == "info" :
                                csvrow['info'] =  value1;
                            else:
                                csvrow[key1] = value1;
                    except:
                        logger.info('Got expection while converting to CSV for key: %s' %(key))
                        # Add a dummy row for convert_row_to_csv(csvrow) call to work
                        csvrow['info'] = "cur: junk; src: junk; dest: junk; upgradeSource: junk;"
                        pass
                else:
                    csvrow[key] = data[key]
            returnval=convert_row_to_csv(csvrow)
            finalVal.append(returnval)
        
    return finalVal
    

def convert_row_to_csv(r):
    import time
    data=(r['info']).split(";")
    for key1 in data:
        if(key1.startswith(" src:")):
            moresplit=key1.split(": ")
            src =moresplit[1]
        elif key1.startswith(" dest:"):
            moresplit=key1.split(": ")
            dest =moresplit[1]
    if 'provisionedTime' in r.keys():
        provisionedTime= time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(r['provisionedTime'])/1000))
        
    else: 
        provisionedTime = 'NO_TIMESTAMP_GIVEN'
    
    if 'Notified' in r.keys():
        notifiedTime= time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(r['Notified'])/1000))
    else: 
        notifiedTime = 'NO_TIMESTAMP_GIVEN'
    
    if 'RequestPermission' in r.keys():
        requestPermissionTime= time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(r['RequestPermission'])/1000))
    else: 
        requestPermissionTime = 'NO_TIMESTAMP_GIVEN'
    
    if 'GettingDescriptor' in r.keys():
        gettingDescriptorTime= time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(r['GettingDescriptor'])/1000))
    else: 
        gettingDescriptorTime = 'NO_TIMESTAMP_GIVEN'
   
    if 'GettingPackage' in r.keys():
        gettingPackageTime= time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(r['GettingPackage'])/1000))
    else: 
        gettingPackageTime = 'NO_TIMESTAMP_GIVEN'
    
    if 'Querying' in r.keys():
        queryingTime= time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(r['Querying'])/1000))
    else: 
        queryingTime = 'NO_TIMESTAMP_GIVEN'
     
    if 'Upgrading' in r.keys():
        upgradingTime= time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(r['Upgrading'])/1000))
    else: 
        upgradingTime = 'NO_TIMESTAMP_GIVEN'
      
    if 'Result_DONE' in r.keys():
        resultDoneTime= time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(r['Result_DONE'])/1000))
    else: 
        resultDoneTime = 'NO_TIMESTAMP_GIVEN'
        
    if 'Result_FAILED' in r.keys():
        resultFailedTime= time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(r['Result_FAILED'])/1000))
    else: 
        resultFailedTime = 'NO_TIMESTAMP_GIVEN'
    
    if 'serialNumber' in r.keys():
        serialNumber =  (r['serialNumber'])
    else: 
        serialNumber = ''
     
    if 'deviceid' in r.keys():
        deviceid =  (r['deviceid'])
    else: 
        deviceid = ''
      
    if 'imei' in r.keys():
        imei =  (r['imei'])
    else: 
        imei = ''
      
    if 'imei_2' in r.keys():
        imei_2 =  (r['imei_2'])
    else: 
        imei_2 = ''
        
    if 'imsi' in r.keys():
        imsi =  (r['imsi'])
    else: 
        imsi = ''
        
    if 'imsi_2' in r.keys():
        imsi_2 =  (r['imsi_2'])
    else: 
        imsi_2 = ''
     
    if 'hwType' in r.keys():
        hwType =  (r['hwType'])
    else: 
        hwType = ''
       
    if 'carrier' in r.keys():
        carrier =  (r['carrier'])
    else: 
        carrier = ''
        
    if 'region' in r.keys():
        region =  (r['region'])
    else: 
        region = ''
       
    if 'android.model' in r.keys():
        androidmodel =  (r['android.model'])
    else: 
        androidmodel = ''
        
    if 'android.carrier' in r.keys():
        androidcarrier =  (r['android.carrier'])
    else: 
        androidcarrier = ''
        
    if 'softwareVersion' in r.keys():
        softwareVersion =  (r['softwareVersion'])
    else: 
        softwareVersion = ''
     
    if 'time' in r.keys():
        time= time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(int(r['time'])/1000))
    else: 
        time = ''
        
    if 'state' in r.keys():
        state =  (r['state'])
    else: 
        state = ''
       
    if 'clientStatus' in r.keys():
        clientStatus =  (r['clientStatus'])
    else: 
        clientStatus = ''
        
    if 'reportingTag' in r.keys():
        reportingTag =  (r['reportingTag'])
    else: 
        reportingTag = ''
        
    if 'trackingId' in r.keys():
        trackingId =  (r['trackingId'])
    else: 
        trackingId = ''
        
    if 'metaDataVersion' in r.keys():
        metaDataVersion =  (r['metaDataVersion'])
    else: 
        metaDataVersion = ''
        
    if 'info' in r.keys():
        info =  (r['info'])
    else: 
        info = ''
        
    if 'deviceInfo' in r.keys():
        deviceInfo =  (r['deviceInfo'])
    else: 
        deviceInfo = ''
      
   
    cols = [    serialNumber, deviceid, imei, imei_2, imsi, imsi_2, 
	            hwType, carrier, region, androidmodel, androidcarrier,
	            provisionedTime, softwareVersion, time, state, clientStatus, src, dest, 
                notifiedTime, requestPermissionTime, gettingDescriptorTime, gettingPackageTime, queryingTime, upgradingTime, 
                resultDoneTime, resultFailedTime, reportingTag, trackingId, metaDataVersion, info, deviceInfo
            ]
    #cols.append('\n')
    return cols
        


def diffrunning(request, format=None):
    pathjson = request.POST['pathjson']
    pk = '1a460d46-05ee-406a-b02d-fcb030e89c68'
    logger.debug("In diffrunning, with json: " + pk)
    try:
        url = '%s/%s' % (PUBLISHEDPATH, pk)
        ppathresp = requests.get(url)
    except ConnectionError:
        return HttpResponseBadRequest('Error connecting to OSM back-end server at %s.  This is recoverable, please retry at a later time.' % PUBLISHEDPATH)
    except URLRequired:
        return HttpResponseBadRequest('Invalid OSM URL %s.  Please reenter a correct one and retry.' % url)
    except:
        if logger.isEnabledFor(logging.DEBUG):
            pprint(sys.exc_info())
            pass
        return HttpResponseBadRequest("Unexpected error:", sys.exc_info()[0])

    if ppathresp.status_code != 200:
        return HttpResponse(status = ppathresp.status_code)

    return HttpResponse(ppathresp.text, mimetype="application/json")

