import sys, requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException, ConnectionError, HTTPError, URLRequired, TooManyRedirects
from pprint import pprint

import httplib

def islog(**kwargs):
    logs = kwargs.get('log', "1")
    return str(logs).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'oh-yeah', 'yeap']
    
'''
Only mandatory argument: zipFileURL.  For GCE Jenkins, this should be something like:
'http://8.35.197.229:8080/userContent/build2/delta-ota-Blur_Version.14.0.539-14.0.548.falcon_umtsds.Brasil.en.BR.zip'
Change portalurl param to point to whichever host:  default: "http://icws-ssota-qa.blurdev.com/autojenkins/"
For localhost: "http://localhost:8080/autojenkins/"
DO NOT FORGET THE TRAILING SLASH
Supply lists like this:
lists='My first list, My second list'
allowpolling=1
allowuser=1
allowsetup=1
'''
def autojenkinswrapped(zipFileUrl, **kwargs):
    log = islog(**kwargs)
    if log:
        httplib.HTTPConnection.debuglevel = 1
        print 'autojenkinswrapped(', zipFileUrl, kwargs, ')'
        pass
    cloudset = kwargs.get('cloudset', 'qa300').lower()
    rawheader = kwargs.get('header', "Authorization: ticket 9S67SlbDVR9XWNnrxMudkfdTX0vrjRaB7TlOkyaGJug=")
    key, value = rawheader.split(':')
    headerdict = {key: value}
    userName = kwargs.get('userName', 'fkr684')
    apitoken = kwargs.get('apitoken', 'OTEzNzNmZmUyMWEwZDNiMjViMzczOTAwMWEwZGQ2OGQK') # On Jenkins in GCE at http://8.35.197.229/
    lists = kwargs.get('lists', '')
    allowpolling = kwargs.get('allowpolling', '')
    allowuser = kwargs.get('allowuser', '')
    allowsetup = kwargs.get('allowsetup', '')
    usecds = kwargs.get('usecds', '1')
    qparams = {
        'zipFileUrl': zipFileUrl,
        'userName': userName,
        'apitoken': apitoken,
        'lists': lists,
        'allowpolling': allowpolling,
        'allowuser': allowuser,
        'allowsetup': allowsetup,
        'usecds' : usecds
        }
    if cloudset == 'qa300':
        portalurl = 'http://icws-ssota-qa.blurdev.com/autojenkins/'
    elif cloudset == 'sdc200':
        portalurl = 'http://upportal-sdc200.blurdev.com/autojenkins/'
    elif cloudset in ('prod', 'dc1', 'dc4'):
        portalurl = 'http://icws-ssota.gtm.svcmot.com/autojenkins/'
    else:
        raise RuntimeError("Unrecognized cloudset '%s'" % cloudset)
    
    # We have all the necessary arguments, now POST
    #res = requests.post(portalurl, headers=headerdict, params=qparams)
    res = requests.post(portalurl, data=qparams)
    if res.status_code != 200:
        raise RuntimeError('Request failed with status code: {status_code}. {message}'.format(status_code=res.status_code, message=res.text))
    try:
        return res.json()['guid']
    except Exception, e:
        raise RuntimeError('Could not extract GUI from server response: %s' % str(e))

if __name__ == '__main__':
    kwargs = {'portalurl': 'http://localhost:8080/autojenkins/', 'allowpolling': 1}
    autojenkinswrapped('http://8.35.197.229:8080/userContent/build2/delta-ota-Blur_Version.14.0.539-14.0.548.falcon_umtsds.Brasil.en.BR.zip', **kwargs)
