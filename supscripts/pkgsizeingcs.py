import requests
import csv
import json
from pprint import pprint

pprint('Opening {} to write'.format('packagesingcs.csv'))
with open('packagesingcs.csv', 'w') as f:
    csvf = csv.DictWriter(f, ('supguid', 'packageguid', 'size'))
    csvf.writeheader()
    pprint('Getting SUPs from SDC200')
    r = requests.get('http://ipws-ssota-sdc200.blurdev.com/upgrade-management/2/upgradepaths/')
    pprint('Loading SUPs from SDC200 into a list')
    sups = json.loads(r.text)
    pprint('Iterating over SUPs')
    for sup in sups:
        pprint(sup)
        break
    pass
