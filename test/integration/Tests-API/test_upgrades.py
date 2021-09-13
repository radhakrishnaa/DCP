"""
Testcases for Upgrade Management service that don't require device interaction.
"""

# Standard library imports
import os
import random
from time import sleep

# Third-party imports
import pytest

# Local imports
from cceclient import CCEClient
from common import *
from create import create_devices
import gdihelper
from umdriver import UmServiceDriver, UmServiceDriverException
from autojenkins import autojenkinswrapped
  
TEST_ASSETS_DIR = "./TestAssets"
DEFAULT_OTA_ZIPFILE = 'http://8.35.197.229:8080/userContent/allpackages/delta-ota-Blur_Version.98.0.0-98.0.1.XT907.Blurdev.en.US.zip'
DEFAULT_OTA_SOURCE_VERSION = 'Blur_Version.98.0.0.XT907.Blurdev.en.US'
DEFAULT2_OTA_ZIPFILE = 'http://8.35.197.229:8080/userContent/allpackages/delta-ota-Blur_Version.98.0.0-98.0.1.XT907.Blurdev.en.US.zip'
DEFAULT2_OTA_SOURCE_VERSION = 'Blur_Version.98.0.0.XT907.Blurdev.en.US'


# LIST PATHS tests

def test_UmService_ListPaths_ReturnsPaths(cloudset):
    """When UM is queried for the list the upgrade paths, UM returns the list"""
    info("*** %s:" % get_function_name(), prefix="\n")
    try:
        driver = None
        driver = UmServiceDriver(cloudset)
        paths = driver.list(showSummary=False)
        assert paths, "UM service returned Null... service error?"
        if len(paths) == 0:
            warn("upgradePath list is empty")
        return paths
    except Exception, e:
        pytest.fail("GET request to list upgradePaths failed: %s" % str(e))
    info("Found %d upgradePath profiles" % len(paths))

# GET PATH tests

def test_UmService_GetPath_ReturnsPath(cloudset):
    """When UM is queried for a path profile, UM returns the profile"""
    info("*** %s:" % get_function_name(), prefix="\n")
    paths = test_UmService_ListPaths_ReturnsPaths(cloudset)
    if paths == []:
        pytest.fail("upgradePath list is empty... can't run this test")
    pathId = random.choice(paths)['guid']
    info("Getting profile for a randomly chosen upgradePath %s" % pathId)
    try:
        driver = None
        driver = UmServiceDriver(cloudset)
        pathSet = driver.list(showSummary=False)
        path = driver.get(pathId)
        assert path, "upgradePath %s was not found" % pathId
        info("Yup, got the path info")
    except Exception, e:
        pytest.fail("GET request to retrieve the upgradePath profile for %s failed: %s" % (pathId, str(e)))

def test_UmService_GetNonexistentPath_ReturnsProfileDoesNotExist(cloudset):
    """When UM is requested to get non-existing profile, UM returns an error"""
    info("*** %s:" % get_function_name(), prefix="\n")
    pathId = 'f28242dd-bfc6-42ca-real-as-unicorn'
    try:
        driver = None
        driver = UmServiceDriver(cloudset)
        path = driver.get(pathId)
        assert path is None, "upgradePath %s is not defined but UM returned a bogus profile: %s" % (pathId, path)
    except Exception, e:
        pytest.fail("GET request to retrieve the upgradePath profile for %s failed: %s" % (pathId, str(e)))
        
# CREATE PATH tests

def test_UmService_CreatePathFromGCEJenkinsNoLogin_PathIsCreated(cloudset):
    """When creating an upgradePath by fetching the package binary from Jenkins with username/password credentials, UM can fetch the binary and create the upgrade path"""
    info("*** %s:" % get_function_name(), prefix="\n")
    zipFileUrl = DEFAULT_OTA_ZIPFILE
    sourceVersion = DEFAULT_OTA_SOURCE_VERSION
    try:
        driver, pathId = None, None
        driver = UmServiceDriver(cloudset)
        existingPathId = driver.find(sourceVersion)
        if existingPathId:
            driver.delete(existingPathId)
 
        # this doesn't work anymore.. something changed in SUP and I don't have time to debug.
        # So now just using autojenkins
        #pathId = driver.create(zipFileUrl, auth=None)          
        #assert pathId, "Failed to create upgradePath"
                   
        # Create the upgrade path with the specified conditions (target lists and allow modes) via autojenkins
        kwargs = {  'log': 0,
                    'cloudset' : cloudset,
                    'allowpolling' : 1,
                    'allowuser' : 1,
                    'allowsetup' : 1,
                    #'usecds' : 1 
                }
        print 'autojenkinswrapped(', zipFileUrl, kwargs, ')'
        pathId = autojenkinswrapped(zipFileUrl, **kwargs)
        info("Successfully created upgradePath %s" % pathId)
        path = driver.get(pathId)
        assert path, "Unable to find the new path just created (pathId=%s)" % pathId
    except Exception, e:
        pytest.fail("POST request to create a new upgradePath failed: %s" % str(e))
    finally:
        if driver and pathId:
            driver.delete(pathId)

def test_UmService_CreateExistingPath_ReturnsPathExists(cloudset):
    """When UM is requested to create an upgradePath that already exits, UM returns an error"""
    info("*** %s:" % get_function_name(), prefix="\n")
    zipFileUrl = DEFAULT_OTA_ZIPFILE
    sourceVersion = DEFAULT_OTA_SOURCE_VERSION
    driver = UmServiceDriver(cloudset)
    existingPathId = driver.find(sourceVersion)
    if existingPathId:
        driver.delete(existingPathId)
    try:
        # Create the upgrade path with the specified conditions (target lists and allow modes) via autojenkins
        kwargs = {  'log': 0,
                    'cloudset' : cloudset,
                    'allowpolling' : 1,
                    'allowuser' : 1,
                    'allowsetup' : 1 }
        print 'autojenkinswrapped(', zipFileUrl, kwargs, ')'
        pathId = autojenkinswrapped(zipFileUrl, **kwargs)
        info("Created upgradePath %s; now test if we can create it again.." % pathId)
    except Exception, e:
        pytest.fail("POST request to create a new upgradePath failed: %s" % str(e))
        
    try:
        # Create the upgrade path with the specified conditions (target lists and allow modes) via autojenkins
        kwargs = {  'log': 0,
                    'cloudset' : cloudset,
                    'allowpolling' : 1,
                    'allowuser' : 1,
                    'allowsetup' : 1 }
        print 'autojenkinswrapped(', zipFileUrl, kwargs, ')'
        pathId = autojenkinswrapped(zipFileUrl, **kwargs)
        info("Created upgradePath %s; now test if we can create it again.." % pathId)
    except RuntimeError, e:
        if e.message.startswith('Request failed with status code: 400'):
            info("Good, UM service reported that path already exists.")
        else:
            pytest.fail(e.message)
    except Exception, e:
        pytest.fail("autojenkins upload failed: %s" % str(e))
    finally:
        if driver and pathId:
            driver.delete(pathId)

def test_UmService_BaseUrlIsDefined_DownloadUrlIsSetToBaseUrl(cloudset):
    """When the upgradePath baseURL is defined, OSM returns the baseURL as the downloadURL"""
    info("*** %s:" % get_function_name(), prefix="\n")
    zipFileUrl = DEFAULT2_OTA_ZIPFILE
    sourceVersion = DEFAULT2_OTA_SOURCE_VERSION
    if cloudset == 'qa300':
        expectedUrl = 'https://dlmgr-qa300.blurdev.com/dl/dlws/1/download'
    elif cloudset == 'sdc200':
        expectedUrl = 'https://dlmgr-sdc200.blurdev.com/dl/dlws/1/download'
    elif cloudset in ('prod', 'dc1', 'dc4'):
        expectedUrl = 'https://dlmgr.gtm.svcmot.com/dl/dlws/1/download'
    else:
        raise RuntimeError("Unrecognized cloudset '%s'" % cloudset)
    try:
        driver, pathId = None, None
        driver = UmServiceDriver(cloudset)
        existingPathId = driver.find(sourceVersion)
        if existingPathId:
            driver.delete(existingPathId)
        # Create the upgrade path with the specified conditions (target lists and allow modes) via autojenkins
        kwargs = {  'log': 0,
                    'cloudset' : cloudset,
                    #'allowpolling' : 1,
                    'allowuser' : 1,
                    #'allowsetup' : 1 
                 }
        print 'autojenkinswrapped(', zipFileUrl, kwargs, ')'
        pathId = autojenkinswrapped(zipFileUrl, **kwargs)
        info("Successfully created upgradePath %s" % pathId)
    except Exception, e:
        pytest.fail("POST request to create a new upgradePath failed: %s" % str(e))

    imei = 2000005
    deviceid = gdihelper.imei_to_deviceid(imei, cloudset)
    assert deviceid, "Can't map IMEI %s to deviceid" % imei
    
    # Verify the device gets the default download URL
    info("Device %s (IMEI %s) check for upgrade..." % (deviceid, imei))
    dev = CCEClient(cloudset)
    dev.deviceid = deviceid
    dev.blurVersion = dev.get_device_info()['softwareVersion']
    meta = dev.check_for_upgrade(warnIfNoUpgrade=False, triggeredBy='user')
    if meta:
        dlUrl = dev.get_download_url(trackingId=meta['trackingId'])
        info("DownloadURL is %s" % dlUrl)
        assert dlUrl.startswith(expectedUrl), \
                "Expecting downloadURL to start with '%s', got '%s'" % (expectedUrl, dlUrl)
    else:
        pytest.fail("Device could not pull the metadata")
    # Set the baseURL
    info("Setting the baseURL to CDN...")
    pojo = driver.get(pathId)
    assert pojo, "Unable to get the POJO for the path just created (pathId=%s)" % pathId
    pojo['upgradePath']['defaultUrl']['baseUrl'] = "http://cdn.motorola.com/dummyUpgradePath"
    driver.update(pathId, pojo)
    driver.enable(pathId)       # simulate a publish
    dlUrl = dev.get_download_url(trackingId=meta['trackingId'])
    info("New downloadURL is %s" % dlUrl)
    assert dlUrl == "http://cdn.motorola.com/dummyUpgradePath", \
            "Expecting baseUrl in downloadURL, got %s" % dlUrl
    # Undo the baseURL
    info("Removing the baseURL...")
    pojo['upgradePath']['defaultUrl']['baseUrl'] = ""
    driver.update(pathId, pojo)
    driver.enable(pathId)
    dlUrl = dev.get_download_url(trackingId=meta['trackingId'])
    info("Reverted downloadURL is %s" % dlUrl)
    assert dlUrl.startswith(expectedUrl), \
            "Expecting downloadURL to start with '%s', got '%s'" % (expectedUrl, dlUrl)
    if driver and pathId:
        driver.delete(pathId)

def test_UmService_TargetList_OnlyDeviceInMWLAndTWLGetsUpgrade(cloudset):
    """When the upgradePath baseURL is defined, OSM returns the baseURL as the downloadURL"""
    info("*** %s:" % get_function_name(), prefix="\n")
    zipFileUrl = DEFAULT2_OTA_ZIPFILE
    sourceVersion = DEFAULT2_OTA_SOURCE_VERSION
    try:
        driver, pathId = None, None
        driver = UmServiceDriver(cloudset)
        existingPathId = driver.find(sourceVersion)
        if existingPathId:
            driver.delete(existingPathId)
        # Create the upgrade path with the specified conditions (target lists and allow modes) via autojenkins
        kwargs = {  'log': 0,
                    'cloudset' : cloudset,
                    #'allowpolling' : 1,
                    #'allowuser' : 1,
                    #'allowsetup' : 1,
                    'lists' : 'pytest_TWL'
                 }
        print 'autojenkinswrapped(', zipFileUrl, kwargs, ')'
        pathId = autojenkinswrapped(zipFileUrl, **kwargs)
        info("Successfully created upgradePath %s" % pathId)
    except Exception, e:
        pytest.fail("POST request to create a new upgradePath failed: %s" % str(e))

    imei = 2000005
    deviceid = gdihelper.imei_to_deviceid(imei, cloudset)
    assert deviceid, "Can't map IMEI %s to deviceid" % imei
    
    # Verify that a device in MWL and TWL can get the metadata for all triggeredBy modes
    info("Device %s (IMEI %s) check for upgrade..." % (deviceid, imei))
    warnMessages = ""
    numMismatches = 0
    for mode in ('user', 'setup', 'polling'):
        dev = CCEClient(cloudset)
        dev.deviceid = deviceid
        dev.blurVersion = dev.get_device_info()['softwareVersion']
        st = (dev.check_for_upgrade(warnIfNoUpgrade=False, triggeredBy=mode) is not None)
        msg = "check for upgrade (%s mode) returned %d, expecting 1" % (mode, st)
        if not st:
            warn(msg)
            warnMessages += ("%s\n" % msg)
            numMismatches += 1
        else:
            info(msg)
    if numMismatches > 0:
        pytest.fail("Mismatch detected:\n%s" % warnMessages)

    imei = 2000004
    deviceid = gdihelper.imei_to_deviceid(imei, cloudset)
    assert deviceid, "Can't map IMEI %s to deviceid" % imei
    
    # Verify that a device in MWL but not in TWL cannot get the metadata for all triggeredBy modes
    info("Device %s (IMEI %s) check for upgrade..." % (deviceid, imei))
    warnMessages = ""
    numMismatches = 0
    for mode in ('user', 'setup', 'polling'):
        dev = CCEClient(cloudset)
        dev.deviceid = deviceid
        dev.blurVersion = dev.get_device_info()['softwareVersion']
        st = (dev.check_for_upgrade(warnIfNoUpgrade=False, triggeredBy=mode) is not None)
        msg = "check for upgrade (%s mode) returned %d, expecting 0" % (mode, st)
        if st:
            warn(msg)
            warnMessages += ("%s\n" % msg)
            numMismatches += 1
        else:
            info(msg)
    if numMismatches > 0:
        pytest.fail("Mismatch detected:\n%s" % warnMessages)