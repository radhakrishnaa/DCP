"""
Testcases for SUPs stored in GCS
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
DEFAULT_OTA_ZIPFILE = 'http://8.35.197.229:8080/userContent/allpackages/delta-ota-Blur_Version.98.6.0-98.6.1.XT907.Blurdev.en.US.zip'
DEFAULT_OTA_SOURCE_VERSION = 'Blur_Version.98.6.0.XT907.Blurdev.en.US'


def _cloudsetToImei(cloudset):
    mapping = {
        'qa300': 990002014021901,
        'sdc200': 990002014021901,  # same IMEI as in QA to try to "trick" OTA service
        'prod': 990002014022503 
    }
    return mapping[cloudset]

def _get_test_settings(cloudset):
    """Return the cloudsets and IMEIs to use for testing.
       The 1st cloudset is already given but we return it for convenience.  
    """
    # For now, I use the same IMEI in all cloudsets. Maybe we should use different IMEIs to
    # make it more realistic ??
    if cloudset == 'qa300':
        cloudset2 = 'sdc200'
    elif cloudset == 'sdc200':
        cloudset2 = 'qa300'  
    elif cloudset in ('prod', 'dc1', 'dc4'):
        cloudset2 = 'sdc200'
    else:
        raise RuntimeError("Unrecognized cloudset '%s'" % cloudset)
    imei, imei2 = _cloudsetToImei(cloudset), _cloudsetToImei(cloudset2)
    return (cloudset, imei, cloudset2, imei2)

def _delete_SUP(cloudset, sourceVersion):
    """Delete SUP from the cloudset if it exists"""
    try:
        driver = UmServiceDriver(cloudset)
        pathId = driver.find(sourceVersion)
        if pathId:
            driver.delete(pathId)
    except Exception, e:
        pytest.fail("Failed to delete path %s on %s: %s" % (pathId, cloudset, str(e)))

def _create_SUP(cloudset, zipFileUrl):
    """Create a SUP on the cloudset"""
    kwargs = {  'log': 0,
                'cloudset' : cloudset,
                'allowpolling' : 1,
                'allowuser' : 1,
                'allowsetup' : 1,
                'usecds' : 1 
             }
    try:
        print 'autojenkinswrapped(', zipFileUrl, kwargs, ')'
        pathId = autojenkinswrapped(zipFileUrl, **kwargs)
        info("Successfully created upgradePath %s on %s" % (pathId, cloudset))
    except Exception, e:
        pytest.fail("POST request to create a new upgradePath on %s failed: %s" % (cloudset, str(e)))
    return pathId

def _verify_ota(cloudset, imei, expectUpgrade, triggeredBy='user'):
    """Verify if device is eligible for and can download the SUP"""
    deviceid = gdihelper.imei_to_deviceid(imei, cloudset)
    assert deviceid, "Can't map IMEI %s to deviceid" % imei
    info("Device %s (IMEI %s) check for upgrade..." % (deviceid, imei))
    dev = CCEClient(cloudset)
    dev.deviceid = deviceid
    dev.blurVersion = dev.get_device_info()['softwareVersion']
    metadata = dev.check_for_upgrade(warnIfNoUpgrade=False, triggeredBy=triggeredBy)
    if expectUpgrade:
        assert metadata, "Device %s (IMEI %s) on %s could not pull the metadata" % (deviceid, imei, cloudset)
        st = dev.download_upgrade(trackingId=metadata["trackingId"])
        assert st, "Device download failed"
    else:
        assert not metadata, "Device %s (IMEI %s) on %s pulled the metadata when it should not: %s" % \
                              (deviceid, imei, cloudset, metadata)


def test_UmService_TwoCloudsetsSharingGcsBucket_DoesNotLeakPackage(cloudset):
    """When two cloudsets share a GCS bucket, a device should not be able to download the 
       SUP from the 2nd cloudset if the SUP was only created on the 1st cloudset.
    """
    info("*** %s:" % get_function_name(), prefix="\n")
    zipFileUrl = DEFAULT_OTA_ZIPFILE
    sourceVersion = DEFAULT_OTA_SOURCE_VERSION
    cloudset, imei, cloudset2, imei2 = _get_test_settings(cloudset)
    for c in (cloudset, cloudset2):
        _delete_SUP(c, sourceVersion)
    
    # Create SUP on 1st cloudset and verify a device on that cloudset can download it
    _create_SUP(cloudset, zipFileUrl)
    info("Verifying device on %s can download the SUP..." % cloudset)
    expectUpgrade = True
    _verify_ota(cloudset, imei, expectUpgrade)

    # Verify a device on the 2nd cloudset CANNOT download the SUP
    info("Verifying device on %s CANNOT download the SUP..." % cloudset2)
    expectUpgrade = False
    _verify_ota(cloudset2, imei2, expectUpgrade)


def test_UmService_TwoCloudsetsSharingGcsBucket_ShouldNotHavePackageConflict(cloudset):
    """When two cloudsets share a GCS bucket and the same SUP is created on both, 
       the two SUPS should be independent and should conflict with each other.
    """
    info("*** %s:" % get_function_name(), prefix="\n")
    zipFileUrl = DEFAULT_OTA_ZIPFILE
    sourceVersion = DEFAULT_OTA_SOURCE_VERSION
    cloudset, imei, cloudset2, imei2 = _get_test_settings(cloudset)
    for c in (cloudset, cloudset2):
        _delete_SUP(c, sourceVersion)
     
    # Create the SUP on both cloudsets
    for cs in (cloudset, cloudset2):
        _create_SUP(cs, zipFileUrl)
    
    # Verify the device on 1st cloudset can download the SUP
    info("Verifying device on %s can download the SUP..." % cloudset)
    expectUpgrade = True
    _verify_ota(cloudset, imei, expectUpgrade)
    
    # Verify the device on 2nd cloudset can download the SUP
    info("Verifying device on %s can also download the SUP..." % cloudset2)
    expectUpgrade = True
    _verify_ota(cloudset2, imei2, expectUpgrade)


def test_UmService_TwoCloudsetsNotSharingGcsBucket_DoesNotLeakPackage(cloudset):
    """When two cloudsets do not share a GCS bucket, a device should not be able to download the 
       SUP from the 2nd cloudset if it was only created on the 1st cloudset.
    """
    info("*** %s:" % get_function_name(), prefix="\n")
    zipFileUrl = DEFAULT_OTA_ZIPFILE
    sourceVersion = DEFAULT_OTA_SOURCE_VERSION
    if cloudset == 'qa300':
        cloudset2 = 'prod'
    elif cloudset == 'sdc200':
        cloudset2 = 'prod'  
    elif cloudset in ('prod', 'dc1', 'dc4'):
        cloudset2 = 'sdc200'
    else:
        raise RuntimeError("Unrecognized cloudset '%s'" % cloudset)
    imei, imei2 = _cloudsetToImei(cloudset), _cloudsetToImei(cloudset2)
    for c in (cloudset, cloudset2):
        _delete_SUP(c, sourceVersion)
    
    # Create SUP on 1st cloudset and verify a device on that cloudset can download it
    _create_SUP(cloudset, zipFileUrl)
    info("Verifying device on %s can download the SUP..." % cloudset)
    expectUpgrade = True
    _verify_ota(cloudset, imei, expectUpgrade)

    # Verify a device on the 2nd cloudset CANNOT download the SUP
    info("Verifying device on %s CANNOT download the SUP..." % cloudset2)
    expectUpgrade = False
    _verify_ota(cloudset2, imei2, expectUpgrade)


