"""Test automation driver for Upgrade Management portal and service"""

# Standard library imports
import os
import pprint
import sys
try: import simplejson as json
except ImportError: import json

# Third-party imports
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException, ConnectionError, HTTPError, URLRequired, TooManyRedirects

# Local imports
from common import info, warn, error, debug, enum
sys.path += ['../../upgrades', '../../upgrades/settings']
import restends     # get cloudset-specific URLs from restends.py (DRY, baby!)
import viewshelper


def default_login():
    """Default login credentials. eg, create(zipFile, auth=default_login())"""
    username = 'hudson'
    apitoken = 'BlurGoat123!'
    return HTTPBasicAuth(username, apitoken)

        
# Custom exceptions
class UmServiceDriverException(Exception):  pass


class UmServiceDriver:
    """Driver for Upgrade Management service"""
    
    def __init__(self, cloudset):
        """Instantiate a UM service driver.
        
        Args:
            cloudset: string, the name of the cloudset to test 
        """
        cloudset = cloudset.lower()
        self.listumUrl = getattr(restends, cloudset.upper() + 'LISTUM')
        self.getumUrl = getattr(restends, cloudset.upper() + 'GETUM')
        self.pmbinariesUrl = getattr(restends, cloudset.upper() + 'PMGETBINARIES')
            
    def list(self, blurVersion=None, product=None, carrier=None, language=None, region=None, showSummary=True):
        """Fetch the list of upgradePaths.
        
        All the filter criteria parameters are optional. Specifying one or more filters will constrain the
        returned items to only those that match the filter values. Typically, one specifies the blurVersion
        or any combination of product/carrier/language/region.
        
        Args:
            product: string, name of product (eg, "XT907")
            carrier: string, carrier name (eg, "Verizon")
            language: string, user language (eg, "en")
            region: string, carrier region (eg, "US")
            blurVersion: string, package version (eg, "Blur_Version.98.0.1.Verizon.en.US")
            showSummary: boolean, setting this flag will print the matched paths to the console
            
        Returns:
            A list of upgrade paths
        """
        url = self.listumUrl
        debug("Getting list of available upgradePaths, listUrl= %s" % url)
        try:
            resp = requests.get(url)
        except Exception, e:
            error("The Http GET call failed: %s" % str(e))
        if resp.encoding is None:
            resp.encoding = 'utf8'
        resp = resp.json()
        if resp['error'] != 'OK':
            raise UmServiceDriverException("Unknown upgradeMgmtService error: %s" % resp['error'])

        paths = resp['profiles']     # note it's plural
        # Filter list by criteria
        if blurVersion:
            paths = [p for p in paths if p['upgradePath']['sourceVersion'] == blurVersion]
        else:
            if product:
                paths = [p for p in paths if p['upgradePath']['match']['hwType'] == product]
            if carrier:
                paths = [p for p in paths if p['upgradePath']['match']['carrier'] == carrier]
            if language:
                paths = [p for p in paths if p['upgradePath']['match']['language'] == language]
            if region:
                paths = [p for p in paths if p['upgradePath']['match']['region'] == region]
        if showSummary:
            for p in paths:
                info(" %s  %s -> %s" % (p['guid'], p['upgradePath']['sourceVersion'], p['upgradePath']['targetVersion']))   
        return paths

    def find(self, blurVersion):
        """Find the upgrade path that matches the given blurVersion.
        
        Args:
            blurVersion: string, the source version to match
        
        Returns:
            The GUID (string) of the matched path, or None if no match found
        """
        paths = self.list(blurVersion=blurVersion, showSummary=False)
        if len(paths) == 1:
            return paths[0]['guid']
        elif len(paths) == 0:
            debug("No upgrade path found that matches source version %s" % blurVersion)
            return None
        else:
            error("Multiple upgrade paths found that source version %s: %s" % (blurVersion, paths))
            return None

    def get(self, pathId):
        """Get the profile of an upgrade path.
        
        Args:
            pathId : string, the unique path identifier
        
        Returns:
            The path profile (metadata), or None if path was not found
        """
        url = self.getumUrl + pathId
        debug("Fetching upgradePath for %s, url= %s" % (pathId, url))
        try:
            resp = requests.get(url)
        except Exception, e:
            error("The Http GET call failed: %s" % str(e))
        resp = resp.json()
        if resp['error'] == 'OK':
            return resp['profile']
        elif resp['error'] == 'DOES_NOT_EXIST':
            return None
        else:
            raise UmServiceDriverException("Unknown upgradeMgmtService error: %s" % resp['error'])

    def create(self, zipFileUrl, auth=default_login()):
        """Create a new upgrade path.
        
        Args:
            zipFileUrl: string, a valid URL pointing to the OTA package .zip file (binary) to use
        
        Returns:
            guid: string, the GUID of the newly created upgrade path.
        """
        zipFileUrl, zipfilename, xmlFileUrl, md5FileUrl = viewshelper._parse_zipfile_url(zipFileUrl)
        try:
            packageId, packageSize = self._upload_package_binary(zipFileUrl, auth)
        except Exception, e:
            raise UmServiceDriverException("Upload package binary failed: %s" % str(e))
        try:
            newpathdict = self._create_upgrade_path(xmlFileUrl, packageId, packageSize, auth)
            guid = self._publish_upgrade_path(newpathdict)
        except Exception, e:
            raise UmServiceDriverException("Create and/or publish upgrade path failed: %s" % str(e))
        return guid

    def update(self, pathId, pathjsondict):
        """Update an upgrade path.
        
        
        Args:
            pathId: string, the GUID of the upgrade path to enable
            pathjsondict: dictionary, the pojo values to apply 
        
        Returns:
            True, if the path got updated. Otherwise throws an exception
        """

        postUrl = self.getumUrl
        debug("Updating upgradePath... posturl= %s" % postUrl)
        headers = {'content-type': 'application/json'}
        data = json.dumps(pathjsondict)
        try:
            resp = requests.put(postUrl + pathId, data=data, headers=headers)
        except Exception, e:
            error("The Http POST call failed: %s" % str(e))
        resp = resp.json()
        if resp['error'] == 'OK':
            return True
        else:
            raise UmServiceDriverException("Unknown upgradeMgmtService error: %s" % resp['error'])
            
    def delete(self, pathId):
        """Delete an upgrade path.
        
        Args:
            pathId: string, the GUID of the upgrade path to delete
        
        Returns:
            True, if the path got deleted. Otherwise throws an exception
        """
        deleteUrl = self.getumUrl + pathId
        info("Deleting upgradePath... deleteUrl= %s" % deleteUrl)
        try:
            resp = requests.delete(deleteUrl)
        except Exception, e:
            error("The Http DELETE call failed: %s" % str(e))
        resp = resp.json()
        if resp['error'] == 'OK':
            return True
        else:
            raise UmServiceDriverException("Unknown upgradeMgmtService error: %s" % resp['error'])

    def enable(self, pathId):
        """Enable an upgrade path.
        
        Change the path's state to 'RUNNING' and update the modified POJO to OSM service.
        
        Args:
            pathId: string, the GUID of the upgrade path to enable
        
        Returns:
            True, if the path got enabled. Otherwise throws an exception
        """
        postUrl = self.getumUrl
        debug("Enabling upgradePath... posturl= %s" % postUrl)
        pathjsondict = self.get(pathId)
        assert pathjsondict, "Failed to get JSON data for %s" % pathId
        pathjsondict['upgradePath']['state'] = 'RUNNING';
        headers = {'content-type': 'application/json'}
        qparams = {'publish': True}
        try:
            resp = requests.put(postUrl + pathId, params=qparams, data=json.dumps(pathjsondict), headers=headers)
        except Exception, e:
            error("The Http POST call failed: %s" % str(e))
        resp = resp.json()
        if resp['error'] == 'OK':
            return True
        else:
            raise UmServiceDriverException("Unknown upgradeMgmtService error: %s" % resp['error'])
            
    def disable(self, pathId):
        """Disable an upgrade path.
        
        Change the path's state to 'STOPPED' and post the modified POJO to OSM service.
        
        Args:
            pathId: string, the GUID of the upgrade path to disable
        
        Returns:
            True, if the path got disabled. Otherwise throws an exception
        """
        postUrl = self.getumUrl
        debug("Disabling upgradePath... posturl= %s" % postUrl)
        pathjsondict = self.get(pathId)
        assert pathjsondict, "Failed to get JSON data for %s" % pathId
        pathjsondict['upgradePath']['state'] = 'STOPPED';
        headers = {'content-type': 'application/json'}
        qparams = {'publish': True}
        try:
            resp = requests.put(postUrl + pathId, params=qparams, data=json.dumps(pathjsondict), headers=headers)
        except Exception, e:
            error("The Http POST call failed: %s" % str(e))
        resp = resp.json()
        if resp['error'] == 'OK':
            return True
        else:
            raise UmServiceDriverException("Unknown upgradeMgmtService error: %s" % resp['error'])

    def download_package_from_GCE(self):
        zipUrl = 'http://173.255.118.170:8080/userContent/build1/delta-ota-Blur_Version.13.0.2720-13.0.2734.ghost_att.ATT.en.US.zip'
        xmlUrl = 'http://173.255.118.170:8080/userContent/build1/Blur_Version.13.0.2720-13.0.2734.ghost_att.ATT.en.US.xml'
        md5Url = 'http://173.255.118.170:8080/userContent/build1/md5sum-hash.txt'
        #return self._download_package(zipUrl, xmlUrl)
        md5 = requests.get(md5Url, stream=True)
        return md5

    ###  Helper methods  ###

    def _upload_package_binary(self, zipFileUrl, auth=None):
        """Fetch the package binary and upload to Package Management Service"""
        debug("Fetching package binary...")
        try:
            rzip = requests.get(zipFileUrl, auth=auth, stream=True)
        except ConnectionError:
            raise UmServiceDriverException('Error connecting to Jenkins server.  This is recoverable, please retry at a later time.')
        except URLRequired:
            raise UmServiceDriverException('Invalid Zip File URL %s.  Please reenter a correct one and retry.' % zipFileUrl)
        except Exception, e:
            raise UmServiceDriverException("Unexpected error: %s" % str(e))
        if rzip.status_code != 200:
            raise UmServiceDriverException('Unable to stream package binary from Jenkins because request to get the file returned in status code: %d' % rzip.status_code )       
        postUrl = self.pmbinariesUrl
        debug("Uploading package binary to Package Management Service... url= %s" % postUrl)
        try:
            pkgresp = requests.post(postUrl, data=rzip)
        except ConnectionError:
            raise UmServiceDriverException('Error connecting to package management server.  This is recoverable, please retry at a later time.')
        except URLRequired:
            raise UmServiceDriverException('Invalid Package Management URL %s.  Correct the settings file used by Django by pointing to valid one' % postUrl)
        except Exception, e:
            raise UmServiceDriverException("Unexpected error: %s" % str(e))

        if pkgresp.status_code != 200:
            raise UmServiceDriverException('Package management server returned status code: %d during streaming of package binary from Jenkins' % pkgresp.status_code )
        pkgresp = pkgresp.json()
        return pkgresp['packageid'], pkgresp['size']
        
    def _get_package_md5(self, zipFileUrl, auth=None):
        zipFileUrl, zipfilename, xmlFileUrl, md5FileUrl = viewshelper._parse_zipfile_url(zipFileUrl)
        try:
            md5sresponse = requests.get(md5FileUrl, auth=auth)
        except ConnectionError:
            raise UmServiceDriverException('Error connecting to Jenkins server.  This is recoverable, please retry at a later time.')
        except URLRequired:
            raise UmServiceDriverException('Invalid MD5 URL %s.  Please log this bug in Jira as syntax for looking up MD5 file has changed and requires update to portal UI code' % md5FileUrl)
        except Exception, e:
            raise UmServiceDriverException("Unexpected error: %s" % str(e))

        md5 = ''
        if md5sresponse.status_code == 200:
            md5s = md5sresponse.text.split()
            for index, item in enumerate(md5s):
                if item.endswith(zipfilename):
                    md5 = md5s[index - 1]
                    break
                pass
            info('MD5 for the file: ' + md5)
            pass
        else:
            warn('Unable to parse MD5 because request to get the MD5 file returned in status code: %d' % md5sresponse.status_code )
        return md5
        
    def _create_upgrade_path(self, xmlFileUrl, packageId, packageSize, auth=None):
        debug("Creating a new upgrade path...")
        try:
            xmldoc = requests.get(xmlFileUrl, auth=auth)
        except ConnectionError:
            raise UmServiceDriverException('Error connecting to Jenkins server.  This is recoverable, please retry at a later time.')
        except URLRequired:
            raise UmServiceDriverException('Invalid XML File URL %s.  Please reenter a correct one and retry.' % xmlFileUrl)
        except Exception, e:
            raise UmServiceDriverException("Unexpected error: %s" % str(e))
    
        if xmldoc.status_code != 200:
            raise UmServiceDriverException('Unable to parse XML because request to get the XML file returned in status code: %d' % xmldoc.status_code )

        newpathdict = dict(viewshelper.AUTOJENKINS_PATH_DICT)
        newpathdict = viewshelper._populate_pojo_dict(newpathdict, xmlFileUrl, xmldoc.text, packageId, packageSize)
        # Add a baseUrl
        #newpathdict["upgradePath"]["defaultUrl"]["baseUrl"] = "http://commondatastorage.googleapis.com/ota-packages%2Fdelta-ota-Blur_Version.98.0.100-98.0.188.XT912.Verizon.en.US.zip"
        viplists, allowpolling, allowuser, allowsetup = None, False, False, False
        newpathdict = viewshelper._populate_autopath_dict(newpathdict, viplists, allowpolling, allowuser, allowsetup)
        debug("Changed POJO to %s" % str(newpathdict))
        return newpathdict
        
    def _publish_upgrade_path(self, pojodict):
        debug("Publishing the upgrade path...")
        postUrl = self.getumUrl
        debug("Uploading path info into Upgrade Management Service... url= %s" % postUrl)
        headers = {'content-type': 'application/json'}
        jsondata = json.dumps(pojodict)
        qparams = {'publish': True}     # Make sure to set this flag, or OSM will not publish the path!
        resp = requests.post(postUrl, params=qparams, data=jsondata, headers=headers)
        resp = resp.json()
        if resp['error'] == 'OK':
            return resp['guid']
        elif resp['error'] == 'ALREADY_EXISTS':
            raise UmServiceDriverException("upgradePath already exists")
        else:
            raise UmServiceDriverException("Unknown upgradeMgmtService error: %s" % resp['error'])
        newpathguid = resp.json().get('guid')
        return newpathguid
