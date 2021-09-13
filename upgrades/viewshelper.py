"""
Helper functions that are used by views.py (in Django context) and automated tester (outside of Django)

"""

import datetime
import os
import re
import time
import logging
from urlparse import urlparse, urlunparse
import xml.etree.ElementTree as ET
from collections import defaultdict

logger = logging.getLogger(__name__)

def _extract_metadata(xmlfilehandle):
    try:
        from xml.etree.cElementTree import iterparse
    except ImportError:
        logger.debug('Using Python Element Tree since cElementTree is unavailable')
        from xml.etree.ElementTree import iterparse
    
    """
    Looking for following tags in XML as metadata
    <flex>Blur_Version.9.2.97.XT925.Brasil.en.BR</flex>
    <fingerprint>motorola/XT925_retbr/vanquish_u:4.1.2/9.8.2Q_94/97:user/release-keys</fingerprint>
    """
    interestingtags = ['flex', 'fingerprint']

    context = iterparse(xmlfilehandle, events=("start", "end"))
        
    # turn it into an iterator
    context = iter(context)
        
    # get the root element
    event, root = context.next()
    metadatadict = defaultdict(str) # In case XML doesn't have all required tags
    for event, elem in context:
        if event == "end":
            try:
                i = interestingtags.index(elem.tag)
            except ValueError:
                continue
            metadatadict[elem.tag] = elem.text
            elem.clear()
            root.clear()
            interestingtags.pop(i)
            if len(interestingtags) == 0:
                # Found all the tags we were looking for
                break
        pass
    # Split the flex into individual chunks
    flavour = major = minor = build = hardware = network = language = region = ''
    if len(metadatadict['flex']) > 0:
        flavour, major, minor, build, hardware, network, language, region = metadatadict['flex'].split('.')
    return metadatadict['flex'], metadatadict['fingerprint'], flavour, major, minor, build, hardware, network, language, region

def _populate_local_pojo_dict(pojodict, zipfilename, packageguid, packagesize, packagemd5, postRequestParams, packagestore):
    
    for key in postRequestParams.POST:
        if key == "Source":
            sourceversion = postRequestParams.POST[key]
        elif key == "FingerPrint":
        	fingerprint = postRequestParams.POST[key]
        elif key == "Target":
        	targetversion = postRequestParams.POST[key]
      	else:
        	value = postRequestParams.POST[key]
        	pojodict['upgradePath']['match'][key] = value
        	print "key: ",key
        	print "val: ",value
        	            
    pojodict['upgradePath']['sourceVersion'] = sourceversion
    pojodict['upgradePath']['targetVersion'] = targetversion
    pojodict['upgradePath']['packageId'] = packageguid
    pojodict['upgradePath']['md5'] = packagemd5
    pojodict['upgradePath']['packageStore'] = packagestore
    pojodict['upgradePath']['packageURL'] = zipfilename
    mdict = pojodict.setdefault('metaData', {})
    # Flavour is picked up as description on older device builds.  Make it empty so it doesn't display on phone during upgrade.
    mdict['flavour'] = ''
    mdict['fingerprint'] = fingerprint
    mdict['minVersion'] = pojodict['upgradePath']['sourceVersion']
    mdict['version'] = pojodict['upgradePath']['targetVersion']
    mdict['size'] = packagesize
    mdict['packageID'] = pojodict['upgradePath']['packageId']
    print "pojoDict ",pojodict
    return pojodict
    
def _populate_pojo_dict_noxml(pojodict, zipfilename, postRequestParams, packageguid, packagesize, packagemd5, packagestore):
    import xml.etree.ElementTree as ET
    
     
    for key in postRequestParams.POST:
        if key == "Source":
            sourceversion = postRequestParams.POST[key]
            pojodict['upgradePath']['sourceVersion'] = sourceversion
        elif key == "FingerPrint":
        	fingerprint = postRequestParams.POST[key]
        elif key == "Target":
        	targetversion = postRequestParams.POST[key]
        	pojodict['upgradePath']['targetVersion'] = targetversion
        elif key == "zipFileUrl":
            test = postRequestParams.POST[key]
        elif key == "userName":
            test = postRequestParams.POST[key]   
        elif key == "apitoken": 
            test = postRequestParams.POST[key] 
        elif key == "usecds": 
            test = postRequestParams.POST[key]    
      	else:
        	value = postRequestParams.POST[key]
        	pojodict['upgradePath']['match'][key] = value
        	print "key: ",key
        	print "val: ",value
        	print "from noxml"
    
    """
    <flavour>Blur_Version</flavour>
    <major>13</major>
    <minor>0</minor>
    <build>2167</build>
    <hardware>ghost_att</hardware>
    <network>ATT</network>
    <language>en</language>
    <region>US</region>
    """
    
    pojodict['upgradePath']['packageId'] = packageguid
    pojodict['upgradePath']['md5'] = packagemd5
    pojodict['upgradePath']['packageStore'] = packagestore
    pojodict['upgradePath']['packageURL'] = zipfilename
    
    mdict = pojodict.setdefault('metaData', {})
    # Flavour is picked up as description on older device builds.  Make it empty so it doesn't display on phone during upgrade.
    mdict['flavour'] = ''
    mdict['fingerprint'] = fingerprint
    mdict['minVersion'] = pojodict['upgradePath']['sourceVersion']
    mdict['version'] = pojodict['upgradePath']['targetVersion']
    mdict['size'] = packagesize
    mdict['packageID'] = pojodict['upgradePath']['packageId']
    return pojodict


def _populate_XMLpojo_dict(pojodict, buildxmlurl, buildxmltext):
    import xml.etree.ElementTree as ET
    print "inside pojodict "
    root = ET.fromstring(buildxmltext)
    """
    <flavour>Blur_Version</flavour>
    <major>13</major>
    <minor>0</minor>
    <build>2167</build>
    <hardware>ghost_att</hardware>
    <network>ATT</network>
    <language>en</language>
    <region>US</region>
    """
    flavour = root.findall('./blurversion/flavour')[0].text
    major = root.findall('./blurversion/major')[0].text
    minor = root.findall('./blurversion/minor')[0].text
    build = root.findall('./blurversion/build')[0].text
    hardware = root.findall('./blurversion/hardware')[0].text
    network = root.findall('./blurversion/network')[0].text
    language = root.findall('./blurversion/language')[0].text
    region = root.findall('./blurversion/region')[0].text
    fingerprint = root.findall('./fingerprint')[0].text

    pojodict['xmlPath']['flex'] = \
      '{flavour}.{major}.{minor}.{build}.{hardware}.{network}.{language}.{region}'.format(
          flavour = flavour, major = major, minor = minor, build = build, hardware = hardware, network = network, language = language, region = region,
          )
    o = urlparse(buildxmlurl)
    tmajor, tminor, tbuild = o.path.split('/')[-1:][0].split('-')[1].split('.')[0:3]
    pojodict['xmlPath']['target'] = \
      '{flavour}.{major}.{minor}.{build}.{hardware}.{network}.{language}.{region}'.format(
          flavour = flavour, major = tmajor, minor = tminor, build = tbuild, hardware = hardware, network = network, language = language, region = region,
          )
   
    pojodict['xmlPath']['hwType'] = hardware
    pojodict['xmlPath']['carrier'] = network
    pojodict['xmlPath']['region'] = region
    pojodict['xmlPath']['fingerprint'] = fingerprint
   
    print "pojodict from jenkins upload: ",pojodict
    return pojodict


def _coercetarget(buildxmlfilename):
    o = re.split('[\.-]', buildxmlfilename)
    if len(o) < 7:
        logger.debug('The filename [{buildxmlfilename}] is NOT a BVS from-to string, so I was unable to split it.  Setting target to empty string'.format(**locals()))
        tmajor = tminor = tbuild = ''
        pass
    else:
        # The filename was a BVS from-to string.
        logger.debug('The filename [{buildxmlfilename}] is a BVS from-to string, so I was able to split it.'.format(**locals()))
        tmajor, tminor, tbuild = o[4:7]
    return tmajor, tminor, tbuild

def _parse_zipfile_url(zipFileUrl):
    # From the package URL, the package filename, the XML filename and MD5 filename are computable
    # Split the Zip File URL into fragments
    #     http://jenkins-main.am.mot.com/view/XLine-Continuous/job/platform_dev_ghost-att_userdebug_main-jb-qcpro-4.2-xline_linux_continuous_OTA/3656/artifact/platform/release/delta-ota-Blur_Version.13.0.2323-13.0.2338.ghost_att.ATT.en.US.zip
    presult = urlparse(zipFileUrl)
    zipfiledir, zipfilename = os.path.split(presult.path)
    pattern = r"""
    ^                              # Expecting a complete string
    (?P<reverse>(reverse)?)        # Reverse delta package?
    (?P<hyphen>(-)?)               # Reverse delta package?
    (?P<deltaprefix>delta-ota-)    # Delta package, right?
    (?P<srctarget>.*)              # BVS including source and target
    (?P<extn>.zip)                 # Must be the ZIP file
    $                              # Expecting a complete string
    """
    bvs_pat = re.compile(pattern, re.VERBOSE)
    mo      = bvs_pat.search(zipfilename)
    if not mo or not mo.group('srctarget'):
        return None

    reverse = '%s%s' % (mo.group('reverse'), '_' if len(mo.group('hyphen')) > 0 else '')
    srctargetstring = mo.group('srctarget')
    extension = '.xml'

    # XML file doesn't have (reverse-)?delta-ota prefix and suffix, naturally is .xml
    # http://jenkins-main.am.mot.com/view/XLine-Continuous/job/platform_dev_ghost-att_userdebug_main-jb-qcpro-4.2-xline_linux_continuous_OTA/3656/artifact/platform/release/Blur_Version.13.0.2323-13.0.2338.ghost_att.ATT.en.US.xml
    xmlFileUrl = urlunparse((presult.scheme, presult.netloc, os.path.join(zipfiledir, '{reverse}{srctargetstring}{extension}'.format(**locals())), presult.params, presult.query, presult.fragment))
    # MD5 file has a constant name
    # http://jenkins-main.am.mot.com/view/XLine-Continuous/job/platform_dev_ghost-att_userdebug_main-jb-qcpro-4.2-xline_linux_continuous_OTA/3656/artifact/platform/release/md5sum-hash.txt
    MD5FILENAME = 'md5sum-hash.txt'
    md5FileUrl = urlunparse((presult.scheme, presult.netloc, os.path.join(zipfiledir, MD5FILENAME), presult.params, presult.query, presult.fragment))
    return (zipFileUrl, zipfilename, xmlFileUrl, md5FileUrl)

def _populate_pojo_dict(pojodict, zipfilename, buildxmlurl, buildxmltext, packageguid, packagesize, packagemd5, packagestore):
    import xml.etree.ElementTree as ET
    root = ET.fromstring(buildxmltext)
    """
    <flavour>Blur_Version</flavour>
    <major>13</major>
    <minor>0</minor>
    <build>2167</build>
    <hardware>ghost_att</hardware>
    <network>ATT</network>
    <language>en</language>
    <region>US</region>
    """
    flavour = root.findall('./blurversion/flavour')[0].text
    major = root.findall('./blurversion/major')[0].text
    minor = root.findall('./blurversion/minor')[0].text
    build = root.findall('./blurversion/build')[0].text
    hardware = root.findall('./blurversion/hardware')[0].text
    network = root.findall('./blurversion/network')[0].text
    language = root.findall('./blurversion/language')[0].text
    region = root.findall('./blurversion/region')[0].text
    fingerprint = root.findall('./fingerprint')[0].text

    pojodict['upgradePath']['sourceVersion'] = \
      '{flavour}.{major}.{minor}.{build}.{hardware}.{network}.{language}.{region}'.format(
          flavour = flavour, major = major, minor = minor, build = build, hardware = hardware, network = network, language = language, region = region,
          )
    o = urlparse(buildxmlurl)
    tmajor, tminor, tbuild = o.path.split('/')[-1:][0].split('-')[1].split('.')[0:3]
    pojodict['upgradePath']['targetVersion'] = \
      '{flavour}.{major}.{minor}.{build}.{hardware}.{network}.{language}.{region}'.format(
          flavour = flavour, major = tmajor, minor = tminor, build = tbuild, hardware = hardware, network = network, language = language, region = region,
          )
    
    pojodict['upgradePath']['packageId'] = packageguid
    pojodict['upgradePath']['md5'] = packagemd5
    pojodict['upgradePath']['packageStore'] = packagestore
    pojodict['upgradePath']['packageURL'] = zipfilename
    pojodict['upgradePath']['match']['hwType'] = hardware
    pojodict['upgradePath']['match']['carrier'] = network
    pojodict['upgradePath']['match']['region'] = region
    mdict = pojodict.setdefault('metaData', {})
    # Flavour is picked up as description on older device builds.  Make it empty so it doesn't display on phone during upgrade.
    mdict['flavour'] = ''
    mdict['fingerprint'] = fingerprint
    mdict['minVersion'] = pojodict['upgradePath']['sourceVersion']
    mdict['version'] = pojodict['upgradePath']['targetVersion']
    mdict['size'] = packagesize
    mdict['packageID'] = pojodict['upgradePath']['packageId']
    return pojodict

def _populate_autopath_dict(pojodict, viplists, allowpolling, allowuser, allowsetup):
    # Start this path a day before right now, same with user and setup allowance
    starton = int(time.mktime((datetime.datetime.utcnow() - datetime.timedelta(days=1)).timetuple()) * 1000)
    if allowpolling:
        pojodict["upgradePath"]["controls"][0]["startDate"] = starton
    else:
        del pojodict["upgradePath"]["controls"][0]
        pass
    
    pojodict["upgradePath"]["userStartTime"] = starton if allowuser else 0
    pojodict["upgradePath"]["setupStartTime"] = starton if allowsetup else 0

    # Setup VIP lists
    if viplists:
        pojodict["upgradePath"].setdefault("listTargets", [])
        pojodict["upgradePath"]["listTargets"].append({
            "startDate": starton,
            "listIds": viplists.split(',')
            })
        pass

    return pojodict


NEW_PATH_DICT = {
  "upgradePath": {
    "defaultUrl": {
      "encrypted": "false",
      "baseUrl": ""
    },
    "controls": [
    ],
    "sourceVersion": "",
    "state": "STOPPED",
    "packageId": "",
    "packageStore": "PM",
    "targetVersion": "",
    "setupStartTime": 0,
    "userStartTime": 0,
    "privateAccessOnly": "true",
    "match": {
    }
  },
  "metaData": {
    "annoy": "60",
    "forced": "true",
    "serviceControlEnabled": "true",
    "flavour": "",
    "installTime": 10,
    "postInstallNotes": "",
    "releaseNotes": "",
    "serviceTimeoutSeconds": 60,
    "wifionly": "true",
    "upgradeNotification": "",
    "version": "",
    "metaVersion": time.time(),
    "continueOnServiceError": "true",
    "downloadOptionsNotes": "",
    "preInstallNotes": "",
    "minVersion": "",
    "extraSpace": 0,
    "size": 0,
    "downloadUrl": "",
    "packageID": "",
    "reportingTag": "",
    "trackingId": "",
    "showPreDownloadDialog": "true",
    "showDownloadOptions": "false",
    "preDownloadNotificationExpiryMins": 1440,
    "preInstallNotificationExpiryMins": 1440,
  }
}


NEW_XMLPATH_DICT = {
  "xmlPath": {  
    "flex": "",
    "target": "",
    "fingerprint": "",
    "hwType": "",
    "carrier": "",
    "region": ""
   }
}

AUTOJENKINS_PATH_DICT = {
    "upgradePath": {
        "defaultUrl": {
            "encrypted": "false",
            "baseUrl": ""
        },
        "targetVersion": "",
        "controls": [
            {
                "startDate": 0,
                "numDays": 365,
                "algorithm": "FLAT_PERCENTAGE",
                "timeSlots": [
                    {
                        "duration": 86400,
                        "start": 0,
                        "percentDownloads": 100
                    }
                ]
            }
        ],
        "sourceVersion": "",
        "state": "RUNNING",
        "userStartTime": 0,
        "packageId": "",
        "packageStore": "PM",
        "setupStartTime": 0,
        "privateAccessOnly": "false",
        "match": {
            "hwType": "",
            "region": "",
            "carrier": ""
        }
    },
    "guid": "",
    "metaData": {
        "serviceControlEnabled": "true",
        "downloadOptionsNotes": "",
        "preInstallNotes": "",
        "serviceTimeoutSeconds": 60,
        "upgradeNotification": "",
        "size": 0,
        "forced": "false",
        "reportingTag": "",
        "version": "",
        "trackingId": "",
        "extraSpace": 0,
        "postInstallNotes": "",
        "packageID": "",
        "releaseNotes": "www.motorola.com",
        "metaVersion": time.time(),
        "fingerprint": "",
        "annoy": "60",
        "flavour": "",
        "installTime": 10,
        "wifionly": "false",
        "downloadUrl": "",
        "continueOnServiceError": "true",
        "minVersion": "",
        "showPreDownloadDialog": "true",
        "showDownloadOptions": "false",
        "preDownloadNotificationExpiryMins": 1440,
        "preInstallNotificationExpiryMins": 1440,
    }
}
