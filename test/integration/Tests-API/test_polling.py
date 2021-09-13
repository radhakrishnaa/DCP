"""
Testcases for polling schedules with Upgrade Management service
"""

# Standard library imports
import datetime
import time
import os
import random
try: import simplejson as json
except ImportError: import json
from time import sleep

# Third-party imports
import pytest

# Local imports
from cceclient import CCEClient
from common import *
from create import create_devices
import gdihelper
from umdriver import UmServiceDriver, UmServiceDriverException
  
SUP_TRUTHTABLE_FILENAME = "Tests-API/SUP_PollTable.csv"
TEST_ASSETS_DIR = "./TestAssets"
UPGRADE_PATH_VERSION = 'Blur_Version.14.0.471-14.0.588.falcon_umts.PollingTest.en.US'
SOURCE_VERSION = 'Blur_Version.14.0.471.falcon_umts.PollingTest.en.US'

lastBaseTime = 0
pathId = ''
pollSuccessSet = set()
nowSeconds = time.time()
lastTimeSlotHours = 0

def _readlines_truthtable(fname):
    """Read the truth table file and serve its entries as data-driven parameters to test_ACL_SUPPollTable().

    Args:
    fname: string, name of the truth table file (.CSV format)

    Returns:
    (list) The entries of the truth table
    """
    lines = []
    with open(fname) as fin:
        for line in fin:
            if not line.startswith("#"):
                lines.append(line.strip())
    return lines

@pytest.mark.parametrize(("truthTableEntry"), _readlines_truthtable(SUP_TRUTHTABLE_FILENAME))
def test_Polling_SUPPollingTable(cloudset, truthTableEntry):

    action,data= truthTableEntry.split(':', 2)
    ACTIONS[action](cloudset,data)

def setTimeAction(cloudset,data):
    global lastBaseTime
    info("setTimeAction data %s" % data)
    lastBaseTime,comment = data.split(',', 2)

def scheduleAction(cloudset,data):
    global lastBaseTime
    global pathId 
    global pollSuccessSet
    global nowSeconds 
    global lastTimeSlotHours
    info("scheduleAction data %s" % data)

    pollSuccessSet = set()
    scheduleStartHoursOffset,scheduleNumDays,timeSlotStartHoursOffset,timeSlotHours,percent,algorithm,comment = data.split(',', 6)
    lastTimeSlotHours = int(timeSlotHours)

    # the schedule startDate is now + start date offset
    starton = (long(lastBaseTime) * 1440 * 60) + long(nowSeconds)
    starton += long(long(scheduleStartHoursOffset)*60*60)
    starton *= 1000

    # the timeslot start is now + start time offset 
    currentSecondsInDay = ((long(nowSeconds)) % (1440 * 60)) + (long(lastBaseTime) * 1440 * 60)
    secondsInDay = long(currentSecondsInDay) + (long(timeSlotStartHoursOffset) * 60 * 60)
    while secondsInDay < 0:
        secondsInDay += 1440 * 60

    secondsInDay = secondsInDay % (1440 * 60)

    editDict = {'startDate': starton, 'numDays': scheduleNumDays, 'algorithm': algorithm, 'timeSlots': [
            {'duration': 60*60*int(timeSlotHours), 'start': secondsInDay, 'percentDownloads': percent} ]}

    driver = UmServiceDriver(cloudset)
    pojo = driver.get(pathId)

    # if the item already exists then delete it (i.e. edit functionality)
    if pojo["upgradePath"]["controls"] and len(pojo["upgradePath"]["controls"]) > 0:
        for index, item in enumerate(pojo["upgradePath"]["controls"]):
            # info("index: %d item %s" % (index,json.dumps(item)))
            if item["startDate"] == starton:
                pojo["upgradePath"]["controls"].remove(item)
                break;

    pojo["upgradePath"]["controls"].append(editDict)
    pojo["upgradePath"]["privateAccessOnly"] = False
    driver.update(pathId, pojo)
    driver.enable(pathId)

def pollAction(cloudset,data):
    global SOURCE_VERSION
    global pollSuccessSet
    global nowSeconds 
    global lastTimeSlotHours

    info("pollAction data %s" % data)

    currentTimeHoursOffset,numDevices,expectedSuccessPercent,expectedPollAfterTime,comment = data.split(',',5)

    pollTime = (long(lastBaseTime) * 1440 * 60) + long(nowSeconds) + (long(currentTimeHoursOffset) * 60 * 60)
    pollTime *= 1000

    dev = CCEClient(cloudset)

    numSuccess = 0
    deviceIndex = 0
    deviceCount = 0
    while deviceCount < int(numDevices):
        while deviceIndex in pollSuccessSet:
            deviceIndex += 1

        serialNumber = '1234009{:04d}9001'.format(deviceIndex)
        dataDict = createDeviceInfo(SOURCE_VERSION,serialNumber)
        st = dev.check_for_upgrade(data=dataDict, warnIfNoUpgrade=False, triggeredBy='polling', pollTime=pollTime)
        if st:
            pollSuccessSet.add(deviceIndex)
            numSuccess += 1

        rslt = json.loads(dev.response)
        acceleratedRate = lastTimeSlotHours * 60 * 60
        if expectedPollAfterTime == "ACCELERATED_POLL_RATE":
            expectedPollAfterTime = str(acceleratedRate) 
        defaultRate = 86400 
        if cloudset == "qa300":
            defaultRate = 360
        if cloudset == "sdc200":
            defaultRate = 3601

        if expectedPollAfterTime == "DEFAULT_POLL_RATE":
            expectedPollAfterTime = str(defaultRate) 
        if expectedPollAfterTime == "MIN_POLL_RATE":
            expectedPollAfterTime = str(min(acceleratedRate,defaultRate)) 
        
        if int(expectedPollAfterTime) != 0:
            pollAfterSeconds = rslt["pollAfterSeconds"]
            assert int(pollAfterSeconds) == int(expectedPollAfterTime), "poll after seconds: %s expected: %s" % (pollAfterSeconds,expectedPollAfterTime)
        # info("check for upgrade returned %s" % json.dumps(rslt))
        deviceIndex += 1
        deviceCount += 1

    successPercent = (float(numSuccess)/float(numDevices)) * 100
    percentDiff = float(successPercent) - float(expectedSuccessPercent)
    assert (-10.0 < percentDiff and percentDiff < 10.0), "success rate: %s expected success rate: %s" % (successPercent,expectedSuccessPercent)


def createSupAction(cloudset,data):
    global pathId
    global UPGRADE_PATH_VERSION 
    info("createSupAction data %s" % data)

    zipFileUrl = 'http://commondatastorage.googleapis.com/com-motorola-cds-test-integration-packages/delta-ota-Blur_Version.14.0.471-14.0.588.falcon_umts.PollingTest.en.US.zip'
    # zipFileUrl = 'http://8.35.197.229:8080/userContent/pytest-build/delta-ota-Blur_Version.14.0.471-14.0.588.falcon_umts.PollingTest.en.US.zip'
    UPGRADE_PATH_VERSION = 'Blur_Version.14.0.471-14.0.588.falcon_umts.PollingTest.en.US'
    try:
        driver, pathId = None, None
        driver = UmServiceDriver(cloudset)
        existingPathId = driver.find(UPGRADE_PATH_VERSION)
        if existingPathId:
            driver.delete(existingPathId)
        pathId = driver.create(zipFileUrl, auth=None)
        assert pathId, "Failed to create upgradePath"
        info("Successfully created upgradePath %s" % pathId)
        path = driver.get(pathId)
        assert path, "Unable to find the new path just created (pathId=%s)" % pathId
    except Exception, e:
        pytest.fail("POST request to create a new upgradePath failed: %s" % str(e))

def removeSupAction(cloudset,data):
    global pathId
    info("removeSupAction data %s" % data)
    driver = UmServiceDriver(cloudset)
    driver.delete(pathId)

def startSupAction(cloudset,data):
    global pathId
    # TODO: not working, fixme
    info("startSupAction data %s" % data)
    driver = UmServiceDriver(cloudset)
    # pojo = driver.get(pathId)
    # driver.update(pathId, pojo)
    driver.enable(pathId)

def stopSupAction(cloudset,data):
    global pathId
    # TODO: not working, fixme
    info("stopSupAction data %s" % data)
    driver = UmServiceDriver(cloudset)
    driver.disable(pathId)

def createDeviceInfo(version,serialNumber):
    parts = version.split('.',8)
    carrier = parts[5]
    region = parts[7]
    model = parts[4]

    dataDict = {
        "currentVersion": SOURCE_VERSION,
        "deviceInfo": {
            "barcode": "FAKEPOLLTESTCCE",
            "language": "en",
            "region": region,
            "serialNumber": serialNumber,
            "softwareVersion": SOURCE_VERSION,
            "hwType": model,
            "extended": "{}",
            "carrier": carrier,
            "imei": serialNumber,
            "osVersion": "4.1.1"
        },
        "deviceid": "123"+serialNumber,
        "triggeredBy": "polling"
        }

    return dataDict

ACTIONS = { 'set_time':setTimeAction, 'schedule':scheduleAction, 'poll':pollAction, 'create_sup':createSupAction, 'remove_sup':removeSupAction, 'start_sup':startSupAction, 'stop_sup':stopSupAction }

