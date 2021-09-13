import urllib2
import json
import zipfile
import re
import time

prodBaseUrl="http://dm.svcmot.com/device_provisioning-1.0/"
qa300Baseurl="http://dm-gsrv-qa300.blurdev.com/device_provisioning-1.0/"
sdc100Baseurl="http://dm-gsrv-sdc100.blurdev.com/device_provisioning-1.0/"
sdc200Baseurl="http://dm-gsrv-sdc200.blurdev.com/device_provisioning-1.0/"


#private static final String SETTINGS_URL = "ws/dm/1/settings";
#private static final String GET_SETTINGS_URL = "ws/dm/1/getsettings";
#private static final String DELETE_SETTINGS_URL = "ws/dm/1/deletesettings";
def _submit_data(filter, settings):
    return json.dumps({"filter": filter, "settings":settings})

def _filter_json(filter):
    return json.dumps({"filter": filter})

def _settings_json(settings):
    return json.dumps({"settings": settings})

def _baseUrl(env):
    if env.lower() == 'prod':
        return prodBaseUrl
    elif env.lower() == 'sdc100':
        return sdc100Baseurl
    elif env.lower() == 'sdc200':
        return sdc200Baseurl
    elif env.lower() == 'qa300':
        return qa300Baseurl
    else:
        return ''

def update_one(env, filter, settings):
    _submit_settings(env, 'PUT', filter, settings)
    
def add_one(env, filter, settings):
    _submit_settings(env, 'POST', filter, settings)
    
def _submit_settings(env, method, filter, settings):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    #
    #Generating the settings version, this should be done inside DP but working around that for now
    #
    settings['settingsVersion'] = settings.get('settingsVersion', str(int(time.time()*1000)))
    data=_submit_data(filter, settings)
    _log('Making call to url- ' + _baseUrl(env)+'ws/dm/1/settings over ' + method )
    _log('Response data-')
    _log(data)
    request = urllib2.Request(_baseUrl(env)+'ws/dm/1/settings', data=data)
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: method
    url = opener.open(request)
    lines = url.readlines()
    jd = json.loads(lines[0] if lines[0] else {})
    if "error" in jd:
        if jd["error"] == "OK":
            return lines[0]
        else:
            _log('Error submitting({2}) settings for the given config {0}. Server returned [{1}]'.format(filter, jd["error_text"] if "error_text" in jd else jd["error"], method ))
    else:
        _log('Error retrieving submitting({2}) for the given config {0}. Server response is [{1}]'.format(filter, lines, method))
    return {}
    
def get(env, **kwargs):
    """
    Gets the settings for a given hwType, carrier, region combination.
    If no filters are specified, it gets the list of all the settings from a given environment.
    """
    if (kwargs):
        rval = _get_settings(env, kwargs)
    else:
        lst = _get_list(env)
        if 'error' in lst:
            return lst
        slist = []
        for l in lst['ids']:
            rset = getbyid(env, l)
            if (rset and ('error' not in rset) and ('settings' in rset) and rset['settings'] != {}):
                slist.append(rset)
            else:
                _log('Error in getting settings for id {0}. Result:{1}'.format(l, rset))
                lst['error'] = lst['error'] if 'error' in lst else [] + [rset['error'] if 'error' in rset else 'Unknown error on getbyid from get']
        rval = lst
    _log(rval)
    return rval

def _get_list(env):
    """
    Gets the list of settings in a given environment.
    """
    retdata = {'environment':env}
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(_baseUrl(env)+'ws/dm/1/settings')
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'GET'
        url = opener.open(request)
        lines = url.readlines()

        jd = json.loads(lines[0] if lines[0] else {})
        if "error" in jd:
            if jd["error"] == "OK":
                if isinstance(jd["settings_ids"], basestring):
                    jd["settings_ids"] = json.loads(jd["settings_ids"])
                retdata['ids'] = jd["settings_ids"]
                return retdata
            else:
                _log('Error retrieving settings list in the given environment {0}. Server returned [{1}]'.format(env, jd["error_text"] if "error_text" in jd else jd["error"] ))
        else:
            _log('Error retrieving settings list in the given environment {0}. Server response is [{1}]'.format(env, lines))
            pass
    except Exception, e:
        _log('Error retrieving settings list in the given environment {0}. Call failed with an exception [{1}]'.format(env, str(e)))
        retdata['error'] = str(e)
    except:
        _log('Error retrieving settings list in the given environment {0}.'.format(env))
        retdata['error'] = 'Unknown error'
    return retdata
    
def getbyid(env, id):
    """
    Gets the settings for a given id.
    """
    result = {'environment':env, 'id':id}
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(_baseUrl(env)+'ws/dm/1/settings/'+id)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'GET'
        url = opener.open(request)
        lines = url.readlines()
        result['settings'] = _extract_settings(lines[0])
        _log(json.dumps(result))
    except Exception, e:
        _log('Error retrieving settings list in the given environment {0}. Call failed with an exception [{1}]'.format(env, str(e)))
        result['error'] = str(e)
    except Error, er:
        _log('Error retrieving settings list in the given environment {0}. Call failed with an error [{1}]'.format(env, str(er)))
        result['error'] = str(er)
    except:
        _log('Error retrieving settings list in the given environment {0}.'.format(env))
        result['error'] = 'Unknown error'
    return result

def _extract_settings(result):
    """
    This method extracts the settings from the response of the settings URI call. The format is expected to be in
    {'error':'OK'}
    """
    jd = json.loads(result if result else {})
    if "error" in jd:
        if jd["error"] == "OK":
            #To workaround the DP bug - needs to get fixed before production rollout
            if isinstance(jd["config"]["settings"], basestring):
                jd["config"]["settings"] = json.loads(jd["config"]["settings"])
            return jd["config"]
        else:
            _log('Error retrieving settings for the given settings id {0}. Server returned [{1}]'.format(id, jd["error_text"] if "error_text" in jd else jd["error"] ))
    else:
        _log('Error retrieving settings for the given settings id {0}. Server response is [{1}]'.format(id, lines))
    return {}
    
def _get_settings(env, filter):
    """
    This method returns a dictionary of {'environment':'', 'filter': {}, 'settings':{}, 'settingId':'', 'version':''}.
    If settings is not found on server then it returns an empty settings data with empty settingId and version.
    If there are any other errors, then the dictionary is returned without the settings
    """
    import types
    retdata = {'environment':env, 'filter':filter}
    _log(retdata)
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        data=_filter_json(filter)
        _log("Making call to url- " + _baseUrl(env)+'ws/dm/1/getsettings ' + 'with data ')
        _log(data)
        request = urllib2.Request(_baseUrl(env)+'ws/dm/1/getsettings', data=data)
        
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'POST'
        url = opener.open(request)
        lines = url.readlines()
        print lines[0]
        jd = json.loads(lines[0] if lines[0] else {})
        if "error" in jd:
            if jd["error"] == "OK":
                #print "SETTINGS>>>", jd
                #To workaround the DP bug - needs to get fixed before production rollout
                if isinstance(jd["config"]["settings"], basestring):
                    jd["config"]["settings"] = json.loads(jd["config"]["settings"])
                retdata.update(jd["config"])
            elif "error_text" in jd and "2 : no any setting for this filter" in jd["error_text"]:
                retdata['settings'] = {}
                retdata['settingId'] = ''
                retdata['version'] = ''
            else:
                _log('Error retrieving settings for the given config {0}. Server returned [{1}]'.format(filter, jd["error_text"] if "error_text" in jd else jd["error"] ))
        else:
            _log('Error retrieving settings for the given config {0}. Server response is [{1}]'.format(filter, lines))
            
    except Exception, e:
        _log('Error retrieving settings list in the given environment {0}. Call failed with an exception [{1}]'.format(env, str(e)))
        retdata['error'] = str(e)
    except Error, er:
        _log('Error retrieving settings list in the given environment {0}. Call failed with an error [{1}]'.format(env, str(er)))
        retdata['error'] = str(er)
    except:
        _log('Error retrieving settings list in the given environment {0}.'.format(env))
        retdata['error'] = 'Unknown error'
    return retdata

def _log(s):
    print s

def _read_props(props):
    """
    Takes a string read from the properties file and converts it to a dictionary of key value.
    Key value have to be on the same line otherwise it will break the parser. 
    """
    pat = re.compile(r'(.*?)=(.*)')
    plines = props.split('\n')
    rdict = {}
    for pl in plines:
        if pl.strip().startswith('#') or len(pl.strip()) == 0: #This is comment or empty line, so ignoring
            continue
        mat = pat.match(pl)
        if not mat:
            _log('[{0}] does not match the property line format.'.format(pl))
            continue
        
        pgrp = mat.groups()
        if len(pgrp) != 2:
            _log('[{0}] does not match the property line format.'.format(pl))
            continue
        #Now we have the two part key and value extract them in to the dictionary
        rdict[pgrp[0]]=_unescape_java_props(pgrp[1])
    return rdict

def _unescape_java_props(st):
    return st.replace('\:', ':')

def _compare_dict(d1, d2):
    #print "d1", d1
    #print "d2", d2
    d3 = d1.copy()
    for k in d2:
        if k in d1: #Key exists in both
            #print "DEBUG>>>", type(k), type(d1), type(d2)
            if d1[k] == d2[k]:
                d3.pop(k) #Values are same so remove the key from this dictionary
            else:
                d3[k] = [d1[k], d2[k]]
        else: #Key does not exist in d1
            d3[k] = [None,d2[k]]
    return d3

def read_from_zip(env, zname, **fter):
    props = read_config_zip(env, zname)
    for f, s in props:
        if fter and fter != f:
            continue
        logdata = {'environment':env, 'filter':f, 'settings':s}
        _log(logdata)
    return props
    
def read_config_zip(env, zname):
    """
    This function for a given environment and the config.zip file, returns a list of tuples of filter and settings
    """
    zf = zipfile.ZipFile(zname)
    ret = zf.testzip()
    if ret is not None:
        _log('Invalid zip file. Info:{0}'.format(ret))
        raise Exception('Invalid zip file for configuration')

    flist = zf.namelist()
    x = 'generic/ws/globsvcs/props/'+env.lower()+'.*properties'
    flist = [f for f in flist if re.match(x, f)]
    proplist = []
    for f in flist:
        parts = f.split('.')
        if len(parts) != 5:
            _log('{0} is not a valid file. File has to be of the 5 part form cfg.Model.Carrier.Region.properties'.format(f))
            continue
        k = {'hwType':parts[1], 'carrier':parts[2], 'region':parts[3]}
        f = zf.open(f)
        fs = f.read()
        props = _read_props(fs)
        proplist = proplist + [(k, props)]
    zf.close()
    #print proplist
    return proplist

def add(env, zname, **fter):
    """
    Adds the settings on a given environment (env) using the values from config.zip (zname)
    Either for all the available filters in config.zip or any supplied filter(fter)
    """
    a = _amod_settings(env, zname, add_one, fter)
    _log(a)

def update(env, zname, **fter):
    """
    Updates the settings on a given environment (env) using the values from config.zip (zname)
    Either for all the available filters in config.zip or any supplied filter(fter)
    """
    a = _amod_settings(env, zname, update_one, fter)
    _log(a)

def _amod_settings(env, zname, mthd, fter):
    import types
    """
    This method
    1. Reads the config.zip(zname) and extracts the settings and forms the filter
    2. If any filter(fter) is specified, applies the setting to just that filter
    3. Otherwise it applies the filter settings
    """
    #print 'METHOD>>>', mthd
    if fter: _log('{1} for filter: {0}'.format(fter, mthd.func_name if type(mthd) == types.FunctionType else 'Add/Update'))
    plist = read_config_zip(env, zname)
    a = []
    for f, s in plist:
        if fter and fter != f:
            continue
        _log('Processing filter: {0}'.format(f))
        mthd(env, f, s)
        srvstg = _compare_single_settings(env, f, s)
        a = a + [srvstg]
    return a

def compare(env, zname, **fter):
    """
    This method compares the settings from the zip file to the environment by querying the settings service.
    If fter is supplied then this method compares the settings between the config file and the server for the given settings,
    If fter is not specified, it performs for all the settings in the config file.
    Return value is a list of
    [{'filter': {'hwType': '201M', 'region': 'JP', 'carrier': 'SBM'}, u'settings': {...}, 'environment': 'qa300', u'settingId': u'873721246849699840', u'version': u'1358323778146_1:null', 'diff': {...}}, ]
    """
    result =  _compare_settings(env, zname, fter)
    _log(result)
    return result

def _compare_single_settings(env, f, s):
    """
    This method compares the settings for a single settings
    """
    srvstg = _get_settings(env, f)
    if 'settings' in srvstg:
        srvstg['diff'] = _compare_dict(srvstg['settings'], s)
    else:
        _log('Error getting settings for {0} from {1}'.format(f, env))
        srvstg['error'] = "Error getting settings from server"
    return srvstg
    
def _compare_settings(env, zname, fter):
    if fter: _log('Comparing for filter: {0}'.format(fter))
    plist = read_config_zip(env, zname)
    a = []
    for f, s in plist:
        if fter and fter != f:
            continue
        _log('Processing filter: {0}'.format(f))
        dset = _compare_single_settings(env, f, s)
        a = a + [dset]
    return a