"""
 for Upgrade Management service
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
SUP_TRUTHTABLE_FILENAME = "Tests-API/SUP_TruthTable.csv"
DEFAULT_OTA_ZIPFILE = 'http://8.35.197.229:8080/userContent/allpackages/delta-ota-Blur_Version.98.0.0-98.0.1.XT907.Blurdev.en.US.zip'
DEFAULT_OTA_SOURCE_VERSION = 'Blur_Version.98.0.0.XT907.Blurdev.en.US'             

# for Prod ?
#DEFAULT_OTA_ZIPFILE = 'http://8.35.197.229:8080/userContent/allpackages/delta-ota-Blur_Version.910.0.0-910.0.1.XT907.Blurdev.en.US.zip'
#DEFAULT_OTA_SOURCE_VERSION = 'Blur_Version.910.0.0.XT907.Blurdev.en.US'

# Helper functions

def _readlines_truthtable(fname):
    """Read the truth table file and serve its entries as data-driven parameters to test_ACL_SUPTruthTable().
    
    Args:
        fname: string, name of the truth table file (.CSV format)

    Returns:
        (list) The entries of the truth table without the header line
    """
    with open(fname) as fin:
        headers = fin.readline()
        if not headers.startswith("MBL"):
            error("Invalid truth table file... first line must contain table header")
        return fin.read().splitlines()

def _select_device(mbl, mwl, tbl, twl, mode='random'):
    """Select a device that is a common member of the given Master or Targeted black/white lists.
    
    This selection algo exploits the IMEI numbering scheme that we setup on QA300.
    *** WILL NOT WORK ON SDC200 because we have not yet created these device account on that cloudset ***
    
    Args:
        mbl, mwl, tbl, twl: integer (0 or 1), 1 means device must be in the list, 0 means must not be in the list.
        mode: string, selection mode if there are multiple matches. NOT IMPLEMENTED
    
    Returns:
        the selected device (IMEI)
    """
    for x in (mbl, mwl, tbl, twl):
        assert x in (0,1), "You must use 0 or 1 to specify whether to include a list"
    idx = 8*mbl + 4*mwl + 2*tbl + twl
    imei = 2000000 + idx
    return imei


@pytest.mark.parametrize(("truthTableEntry"), _readlines_truthtable(SUP_TRUTHTABLE_FILENAME))
def test_ACL_SUPTruthTable(cloudset, truthTableEntry):
    """Verify that SUP and OSM correctly manages device access to upgrade paths.
    
       We use py.test's parametrization feature (http://pytest.org/latest/parametrize.html) to rerun this test
       against different inputs. Each line in the Truth Table file contains the test conditions and expected
       results, in this format:
         MBL,MWL,TBL,TWL, allowpoll,allowser,allowsetup, expectedpoll,expecteduser,expectedsetup
        
       The first 4 columns specify whether a Master Blacklist, Targeted Blacklist, Master Whilelist and 
       Targeted Whitelist respectively are to be associated to the upgrade path. The 3 'allow' columns specify
       whether to enable those modes in the POJO. The 3 'expected' columns indicate what the behavior we expect
       if the device attempts to upgrade in those various modes.
    """
    info("*** %s:" % get_function_name(), prefix="\n")
    # Get the package binary from GCE Jenkins so we don't have to worry about packages getting purged
    zipFileUrl = DEFAULT_OTA_ZIPFILE
    sourceVersion = DEFAULT_OTA_SOURCE_VERSION
    listNames = {'mbl':'pytest_MBL', 'tbl':'pytest_TBL', 'twl':'pytest_TWL'}

    # Find a device that satisfies the test conditions specified in the truth table entry
    vals = truthTableEntry.split(',', 9)
    vals = map(lambda x: int(x) if x in ('0','1') else x, vals)
    mbl,mwl,tbl,twl,allowpoll,allowuser,allowsetup,expectedpoll,expecteduser,expectedsetup = vals
    expected = {'polling':expectedpoll, 'user':expecteduser, 'setup':expectedsetup}
    imei = _select_device(mbl, mwl, tbl, twl)
    assert imei, "No matching device found for given lists"
    deviceid = gdihelper.imei_to_deviceid(imei, cloudset)
    assert deviceid, "Can't map IMEI %s to deviceid" % imei
    numMismatches = 0
    try:
        driver, pathId = None, None
        driver = UmServiceDriver(cloudset)
        existingPathId = driver.find(sourceVersion)
        if existingPathId:
            info("Path exists for %s... deleting" % sourceVersion)
            driver.delete(existingPathId)
        else:
            info("No exisiting path for %s" % sourceVersion)
        # Create the upgrade path with the specified conditions (target lists and allow modes) via autojenkins
        kwargs = { 'log' : 0, 
                   'cloudset' : cloudset }
        if allowpoll:
            kwargs['allowpolling'] = 1
        if allowuser:
            kwargs['allowuser'] = 1
        if allowsetup:
            kwargs['allowsetup'] = 1
        
        # Associate the list(s) with the upgrade path. Not needed for MWL devices since 
        # they are already permanently whitelisted.
        supLists = []
        if mbl:
            supLists.append(listNames['mbl'])
        if tbl:
            supLists.append(listNames['tbl'])
        if twl:
            supLists.append(listNames['twl'])
        if supLists:
            kwargs['lists'] = ','.join(supLists)
        print 'autojenkinswrapped(', zipFileUrl, kwargs, ')'
        autojenkinswrapped(zipFileUrl, **kwargs)
        pathId = driver.find(sourceVersion)
        info("PathId = %s" % pathId)
        if not pathId:
            warn("Can't find upgradePath.. failed to upload %s?" % sourceVersion)
            sleep(5)
            pathId = driver.find(sourceVersion)
            info("PathId = %s" % pathId)
            assert pathId, "Can't find upgradePath.. failed to upload %s?" % sourceVersion
        info("Lists attached: MBL=%d TBL=%d MWL=%d TWL=%d" % (mbl, tbl, mwl, twl))
    except Exception, e:
        pytest.fail("POST request to create a new upgradePath failed: %s" % str(e))

    # Check if the device can get the package metadata for all triggeredBy modes
    info("IMEI %s (deviceid %s) check for upgrade..." % (imei, deviceid))
    warnMessages = ""
    for mode in ('polling', 'user', 'setup'):
        dev = CCEClient(cloudset)
        dev.deviceid = deviceid
        dev.blurVersion = dev.get_device_info()['softwareVersion']
        st = (dev.check_for_upgrade(warnIfNoUpgrade=False, triggeredBy=mode) is not None)
        msg = "check for upgrade (%s mode) returned %d, expecting %d" % (mode.upper(), st, expected[mode])
        if st != expected[mode]:
            warn(msg)
            warnMessages += ("%s\n" % msg)
            numMismatches += 1
        else:
            info(msg)
    if numMismatches > 0:
        pytest.fail("Mismatch detected:\n%s" % warnMessages)

    
def test_ACL_GetLists_ReturnsLists(cloudset):
    """When UM is queried for the available target and master lists, UM returns the lists"""
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


