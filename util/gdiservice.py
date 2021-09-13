import urllib2
import json
import zipfile
import re
import time
import logging
import types
import logging.config

ENV_URLS = {
    'prod': 'http://iapi.svcmot.com',
    'sdc100': 'http://imapi-sdc100.blurdev.com',
    'sdc200': 'http://imapi-sdc200.blurdev.com',
    'qa300': 'http://imapi-qa300.blurdev.com',
}
APP_ID = "R6LQQA7YR3B8XFV1PRPMBXIR8V6QBIWT"

logger = logging.getLogger()


def _clean_filter(settings_filter):
    return dict((k, v) for k, v in settings_filter.iteritems() if v)


def _submit_data(settings, settings_filter):
    return json.dumps({
        "settings": settings,
        "filter": _clean_filter(settings_filter),
    })


def _filter_json(settings_filter):
    return json.dumps({
        "filter":  _clean_filter(settings_filter),
    })


def _base_url(env):
    if env not in ENV_URLS:
        raise Exception('Unable to find URL for environment %r' % env)
    return ENV_URLS.get(env, '')


def update_one(env, settings_filter, settings):
    return _submit_settings(env, 'PUT', settings_filter, settings)


def add_one(env, settings_filter, settings):
    return _submit_settings(env, 'POST', settings_filter, settings)


def _submit_settings(env, method, settings_filter, settings):
    opener = urllib2.build_opener(urllib2.HTTPHandler)

    # generating the settings version, this should be done inside DP but
    # working around that for now
    settings['settingsVersion'] = settings.get('settingsVersion',
                                               str(int(time.time() * 1000)))
    url = _base_url(env) + '/v1/gsa/settings.json?appid=' + APP_ID
    data = _submit_data(settings, settings_filter)
    logger.info('SUBMIT_SETTINGS %s %s => %r' % (method, url, data))
    request = urllib2.Request(url, data)
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: method
    url = opener.open(request)
    lines = url.readlines()
    jd = json.loads(lines[0] if lines[0] else {})

    logger.debug('Response of submit operation:')
    logger.debug(jd)
    if "error" in jd:
        if jd["error"] == "OK":
            return lines[0]
        logger.error('Error submitting(%r) settings for the given config %r. '
                     'Server returned [%r]', method, settings_filter,
                     jd["error_text"] if "error_text" in jd else jd["error"])
    else:
        logger.error(
            'Error retrieving submitting(%r) for the given config %r. '
            'Server response is [%r]', method, settings_filter, lines)
    return {}


def get_settings(env, **kwargs):
    """
    Gets the settings for a given hwType, carrier, region combination.
    """
    r = _get_settings(env, kwargs)
    if 'settings' not in r:
        raise Exception('Unexpected response from GDI service: %r' % r)
    return r['settings']


def get_settings_by_id(env, id):
    """
    Gets the settings for a given id.
    """
    result = {'environment': env, 'id': id}
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request_url = _base_url(env) + '/v1/gsa/settings.json/' + str(id)
        logger.debug('get settings by id (%r) GET %r' % (id, request_url))
        request = urllib2.Request(request_url)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'GET'
        url = opener.open(request)
        lines = url.readlines()
        logger.debug('get settings by id (%r, %r) return: %r' % (
            id, env, lines))
        result['settings'] = _extract_settings(lines[0])
        logger.debug(json.dumps(result))
    except Exception, e:
        logger.debug('Error retrieving settings list in given environment %r. '
                     'Call failed with an exception [%r]', env, e)
        result['error'] = str(e)
    return result


def _extract_settings(result):
    """
    This method extracts settings from response of settings URI call.
    The format is expected to be like {'error':'OK'}
    """
    jd = json.loads(result if result else {})
    if "error" not in jd or jd["error"] != "OK":
        logger.debug('Error retrieving settings for the given settings. '
                     'Server response: %r', jd)
        return {}
    # To workaround DP bug: needs to get fixed before production rollout
    if isinstance(jd["config"]["settings"], basestring):
        jd["config"]["settings"] = json.loads(jd["config"]["settings"])
    return jd["config"]


def _get_settings(env, settings_filter):
    """
    This method returns a dictionary of {
        'environment':'',
        'filter': {},
        'settings':{},
        'settingId':'',
        'version':''
    }.
    If settings is not found on server then it returns an empty settings data
    with empty settingId and version. If there are any other errors, then the
    dictionary is returned without the settings
    """
    ret_data = {'environment': env, 'filter': settings_filter}
    logger.info('ret_data before downloading settings: %r', ret_data)
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        url = _base_url(env) + '/v1/gsa/settings/query.json?appid=' + APP_ID
        data = _filter_json(settings_filter)
        logger.debug('get settings - POST %s %r', url, data)
        request = urllib2.Request(url, data=data)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'POST'
        url = opener.open(request)
        lines = url.readlines()
        jd = json.loads(lines[0] if lines[0] else {})
        if "error" not in jd:
            logger.debug('Error retrieving settings for the given config %r. '
                         'Server response: %r', settings_filter, lines)
            return ret_data
        if jd["error"] == "OK":
            # To workaround DP bug: fix needed before production rollout
            if 'settings' in jd.keys():
                if isinstance(jd["settings"], types.DictType):
                    ret_data.update({"settings": jd["settings"]})
            else:
                logger.debug("No settings present")
                ret_data.update({"settings": {}})
                logger.debug("retdata after update")
                logger.debug(ret_data)
                logger.debug("------")
        elif ("error_text" in jd and
              '2 : no any setting for this filter' in jd["error_text"]):
            ret_data['settings'] = {}
            ret_data['settingId'] = ''
            ret_data['version'] = ''
        else:
            logger.debug(
                'Error retrieving settings for the given config %r. Server'
                ' returned [%r]', settings_filter,
                jd["error_text"] if "error_text" in jd else jd["error"])
    except Exception, e:
        logger.debug('Error retrieving settings list in given environment %r. '
                     'Call failed with an exception [%r]', env, e)
        ret_data['error'] = str(e)
    return ret_data


def _read_props(props):
    """
    Takes a string read from properties file and converts it to a dictionary of
    key value. Key value have to be on same line otherwise it will break parser.
    """
    pat = re.compile(r'(.*?)=(.*)')
    plines = props.split('\n')
    rdict = {}
    for pl in plines:
        if pl.strip().startswith('#') or len(
                pl.strip()) == 0:  # This is comment or empty line, so ignoring
            continue
        mat = pat.match(pl)
        if not mat:
            logger.error('[%r] does not match property line format', pl)
            continue

        pgrp = mat.groups()
        if len(pgrp) != 2:
            logger.error('[%r] does not match property line format', pl)
            continue
        # Now we have two part key and value extract them in to the dictionary
        rdict[pgrp[0]] = _unescape_java_props(pgrp[1])
    return rdict


def _unescape_java_props(st):
    return st.replace('\:', ':')


def _compare_dict(d1, d2):
    d3 = d1.copy()
    for k in d2:
        if k in d1:  # Key exists in both
            if d1[k] == d2[k]:
                d3.pop(k)  # Values are same so remove key from this dictionary
            else:
                d3[k] = [d1[k], d2[k]]
        else:  # Key does not exist in d1
            d3[k] = [None, d2[k]]
    return d3


def read_from_zip(env, zname, **fter):
    props = read_config_zip(env, zname)
    for f, s in props:
        if fter and fter != f:
            continue
        logdata = {'environment': env, 'filter': f, 'settings': s}
        logger.info(logdata)
    return props


def read_config_zip(env, zname):
    """
    This function for a given environment and the config.zip file, returns a
    list of tuples of filter and settings.
    """
    zf = zipfile.ZipFile(zname)
    ret = zf.testzip()
    if ret is not None:
        logger.error('Invalid zip file. Info: %r', ret)
        raise Exception('Invalid zip file for configuration')

    flist = zf.namelist()
    x = 'generic/ws/globsvcs/props/' + env.lower() + '.*properties'
    flist = [f for f in flist if re.match(x, f)]
    proplist = []
    for f in flist:
        parts = f.split('.')
        if len(parts) != 5:
            logger.error('%r is not a valid file. File has to be of the 5 part '
                         'form cfg.Model.Carrier.Region.properties', f)
            continue
        k = {'hwType': parts[1], 'carrier': parts[2], 'region': parts[3]}
        f = zf.open(f)
        fs = f.read()
        props = _read_props(fs)
        proplist = proplist + [(k, props)]
    zf.close()
    return proplist


def add(env, zname, **fter):
    """
    Adds the settings on a given environment (env) using the values from
    config.zip (zname) Either for all the available filters in config.zip or any
     supplied filter(fter)
    """
    a = _amod_settings(env, zname, add_one, fter)
    logger.info('add(): %r', a)


def update(env, zname, **fter):
    """
    Updates the settings on a given environment (env) using the values from
    config.zip (zname) Either for all the available filters in config.zip or any
    supplied filter(fter)
    """
    a = _amod_settings(env, zname, update_one, fter)
    logger.info('update(): %r', a)


def _amod_settings(env, zname, mthd, fter):
    """
    This method
    1. Reads config.zip(zname), extracts settings and forms filter
    2. If any filter(fter) is specified, applies setting to just that filter
    3. Otherwise it applies the filter settings
    """
    if fter:
        logger.info('%r for filter: %r', fter,
                    mthd.func_name if isinstance(mthd, types.FunctionType)
                    else 'Add/Update')
    plist = read_config_zip(env, zname)
    a = []
    for f, s in plist:
        if fter and fter != f:
            continue
        logger.info('Processing filter: %r', f)
        mthd(env, f, s)
        srvstg = _compare_single_settings(env, f, s)
        a = a + [srvstg]
    return a


def compare(env, zname, **fter):
    """
    This method compares the settings from the zip file to the environment by
    querying the settings service. If fter is supplied then this method compares
    the settings between the config file and the server for the given settings,
    If fter is not specified, it performs for all the settings in the config
    file.
    Return value is a list of [{
        'filter': {'hwType': '201M', 'region': 'JP', 'carrier': 'SBM'},
        u'settings': {...},
        'environment': 'qa300',
        u'settingId': u'873721246849699840',
        u'version': u'1358323778146_1:null',
        'diff': {...}
    }, ]
    """
    result = _compare_settings(env, zname, fter)
    logger.info('%r', result)
    return result


def _compare_single_settings(env, f, s):
    """
    This method compares the settings for a single settings.
    """
    srvstg = _get_settings(env, f)
    if 'settings' in srvstg:
        srvstg['diff'] = _compare_dict(srvstg['settings'], s)
    else:
        logger.error('Error getting settings for %r from %r', f, env)
        srvstg['error'] = "Error getting settings from server"
    return srvstg


def _compare_settings(env, zname, fter):
    if fter:
        logger.error('Comparing for filter: %r', fter)
    plist = read_config_zip(env, zname)
    a = []
    for f, s in plist:
        if fter and fter != f:
            continue
        logger.debug('Processing filter: %r', f)
        dset = _compare_single_settings(env, f, s)
        a = a + [dset]
    return a
