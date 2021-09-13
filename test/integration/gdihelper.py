import httplib, urllib
import json
import uuid
    
def_headers = {"Content-type": "application/json", "Accept": "text/plain"}
conn_map = {}

def connect(forced = False, **kwargs):
    srvr = kwargs.get('server', "idi-gdi-qa300.blurdev.com")
    if forced:
        conn_map.pop(srvr, None)
    return conn_map.setdefault(srvr, httplib.HTTPConnection(srvr))

def wscall(method, path, data=None, headers=def_headers, **kwargs):
    log = islog(**kwargs)
    if log:
        print method, kwargs
    response = None
    retry = 5
    while retry > 0:
        try:
            srvr = kwargs.get('server', "idi-gdi-qa300.blurdev.com")
            if log:
                print "connecting to server:", srvr
            
            conn = kwargs.setdefault('connection', httplib.HTTPConnection(srvr))
            conn.request(method, path, data, headers)
            response = conn.getresponse()
            break
        except httplib.BadStatusLine:
            print "Connect error"
            retry = retry + 1
            kwargs.pop('connection', None)
            
    if not response:
        print "Error getting response", method, path, data
        return []
    if log:
        print response.status, response.reason
    rdata = response.read()
    if log:
        print "RDATA", rdata
    if response.status == 200:
        return json.loads(rdata)
    else:
        return {}

def islog(**kwargs):
    logs = kwargs.get('log', "1")
    return str(logs).lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'oh-yeah', 'yeap']
    
def getdinfo(device_ids, **kwargs):
    if not device_ids:
        raise Exception("Please provide the device_ids to get the device info")
    data = json.dumps({"deviceIds":device_ids})
    response = wscall("POST", "/device_identity-1.0/ws/di.json/1/getbatchdevice", data, **kwargs)
    return response.get('devices', [])
    
def resolve_imei(imei, **kwargs):
    if not imei:
        raise Exception("IMEI is not proviced. Please provide a valid input")
    response = wscall("GET", "/device_identity-1.0/ws/di.json/1/querybycriteria/imei/"+imei, None, **kwargs)
    if "error" not in response or "OK" != response["error"]:
        raise Exception("Error retrieving the imei list from server")
    retval = {}
    if "deviceIds" in response and len(response["deviceIds"]) > 0:
        devices = getdinfo(response["deviceIds"], **kwargs)
        latest = None
        for dev in devices:
            if "fields" in dev and "loginTime" in dev["fields"]:
                if latest is None or latest["fields"]["loginTime"] <= dev["fields"]["loginTime"]:
                    latest = dev
        if latest:
            retval["latest"] = latest
        retval['devices'] = devices
    else:
        retval['message'] = 'No devices found for imei:'+imei
    #print retval
    return retval

def imei_to_deviceid(imei, cloudset, log=False):
    """Wrapper to ease mapping IMEI-to-(latest)deviceId"""
    cloudset = cloudset.lower()
    if cloudset == 'prod' or cloudset.startswith('dc'):
        gdihost = "gdi-gsrv.svcmot.com"
    else:
        gdihost = "idi-gdi-"+cloudset+".blurdev.com"
    try:
        rslt = resolve_imei(imei=str(imei), server=gdihost, log=log)['latest']
        return int(rslt['fields']['guid'])
    except Exception, e:
        return None

def getbatch(batch_request= None, **kwargs):

    if batch_request:
        kwargs['batch_request'] = batch_request
    log = islog(**kwargs)
    if log:
        print kwargs
    ds = getrange(**kwargs)
    kwargs['batch_request'] = json.dumps({'deviceIds':ds})
    data = kwargs.get("batch_request", """{"deviceIds":["873728273359024128","873728273377869824","873728273477505024"]}""")
    response = wscall("POST", "/device_identity-1.0/ws/di.json/1/getbatchdevice", data, **kwargs)
    return response.get('devices', [])



def getimeis(**kwargs):
    import time
    fname = kwargs.get('swversion','') + '.'+ str(int(time.time())) + '.imei'
    f = open(fname, 'w')
    respj = getbatch(None, **kwargs)
    if (respj and len(respj) > 0) :
        for d in respj:
            fields = d['fields']
            s = fields.get('imei') + ',' + fields.get('cloudName', 'NotAvailable') + '\r\n'
            f.write(s)
    f.close()

def getrange(**kwargs):
    from datetime import datetime
    import time
    cdate = datetime.now()
    ctime = time.mktime(cdate.timetuple())
    fromtime = ctime - int(kwargs.get('hours_back', 24))*60*60
    swversion = kwargs.get('swversion',None)
    queryby = kwargs.get('queryby', 'creationTime')
    path =  "/device_identity-1.0/ws/di.json/1/querybyrange/"+queryby+"/"+str(int(fromtime)*1000)+"/"+str(int(ctime)*1000)+ ("/"+swversion if swversion is not None else '')
    print "PATH:", path
    data = wscall("GET", path, **kwargs)
    devices = data.get("deviceIds", [])
    return devices


def loop_range(hours_back=24, iter=1, log = True, server='idi-gdi-qa300.blurdev.com', **kwargs):
    kwargs['iter'] = iter
    kwargs['log'] = log
    kwargs['server'] = server
    kwargs['hours_back'] = hours_back
    loop_method(getrange, **kwargs)

def loop_batch(iter=1, log = True, server='idi-gdi-qa300.blurdev.com', **kwargs):
    kwargs['iter'] = iter
    kwargs['log'] = log
    kwargs['server'] = server
    loop_method(getbatch, **kwargs)

def loop_method(method, **kwargs):
    import time, sys
    from datetime import datetime

    iters = int(kwargs.get('iter', 1))
    print "Iterations:", iters, "Starting at:", datetime.now()
    stats = []
    start = time.time()
    for i in xrange(0,iters):
        start = time.time()
        ds = method(**kwargs)
        stats.append((len(ds), (time.time() - start)))
        print '.',
        time.sleep(0.01)
    print '\r\nEnd', datetime.now()
    print 'Stats:', method.__name__, ':', stats

def tail_logs():
    from fabric.api import run
    run('tail -100 /home/jetty/current/logs/log4j*.log')
    

#dsess = create_device()
#print dsess['deviceId']

