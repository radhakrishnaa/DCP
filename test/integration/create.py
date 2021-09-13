# create.py -- create one or more CCE devices

from common import *
from time import sleep, time
from cceclient import CCEClient


CLOUDSETS = ['qa300', 'sdc100', 'sdc200']
CREATE_INTERVAL_TIME=5              # seconds between account creation

def create_devices(cloudset, blurVersion, imeiFileOrList=None, count=None):
    assert ((imeiFileOrList != None and count is None) or (imeiFileOrList is None and count != None)), \
            "You must give either an IMEI list/file or a count parameter (and don't give both)"
    assert imeiFileOrList is None or isinstance(imeiFileOrList, (str, list, tuple)), \
            "Expecting an IMEI list or file... did you mean to use the count=N option?"
    cloudset = cloudset.lower()
    debug("cloudset=%s  blurVersion=%s  imeilist=%s"  % (cloudset, blurVersion, imeiFileOrList))
    if not cloudset in CLOUDSETS:
        error("Cloudset must be one of: %s" % CLOUDSETS)
    try:
        device = CCEClient(cloudset, defaults_file="default_params_cce.txt")
    except Exception, e:
        error(e)

    newDeviceImeis = []
    if count:  # create 'count' devices and generate the IMEIs for each one
        for i in range(count):
            sleep(0.1)
            imei = '9'+str(long(time()*1000))
            if create1(device, cloudset, blurVersion, imei):
                newDeviceImeis.append(imei)
    elif isinstance(imeiFileOrList, (list,tuple)):  # create devices using given IMEI list
        imeiInputList = imeiFileOrList
        for imei in imeiInputList:
            if create1(device, cloudset, blurVersion, imei):
                newDeviceImeis.append(imei)    
    else:  # create devices using the IMEIs contained in the given file
        imeiFile = imeiFileOrList
        for line in open(imeiFile, 'r'): 
            imei = line.strip()
            if imei != "" and create1(device, cloudset, blurVersion, imei):
                newDeviceImeis.append(imei)
    return newDeviceImeis

def create1(device, cloudset, blurVersion, imei):
    imei = str(imei)        
    try:
        device.newaccount(blurVersion=blurVersion, imei=imei)
        info("Successfully created a CCE device for IMEI %s" % imei)
        return True
    except Exception, e:
        warn("Failed to create a CCE device for IMEI %s: %s" % (imei, e))
        return False  

    
    




