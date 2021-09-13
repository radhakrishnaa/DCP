from upgrades.views import _editpath, GETUM
from pprint import pprint
import requests
import argparse
import json

sup = '91991b87-0f11-4ef9-b583-2b60f153a1fe'
pprint('Starting to empty out flavour on production for SUP: {sup}'.format(**locals()))

def emptyflavour(sup=sup):
    response = requests.get(GETUM + sup)
    html = json.loads(response.text)
    html = response.json()
    if html.has_key('error') and html['error'] == 'DOES_NOT_EXIST':
        e = 'SUP with guid:{sup} does not exist -- perhaps someone deleted it?'.format(**locals())
        pprint(e)
        return
    ps = html.get('profile')
    if ps['guid'] != sup:
        pprint('Hmm, got wrong SUP for the supplied GUID.  Strange.  Existing')
        return
    pprint(ps)
    ps['metaData']['flavour'] =	''
    pprint(ps)
    _editpath(ps)
    pass

emptyflavour()
