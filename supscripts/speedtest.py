import requests

# Standard library imports
import os, json, urllib2, logging, base64, pdb, requests, re, time, datetime, copy, sys
from datetime import datetime
import io
from pprint import pprint
from memory_profiler import profile

GETPACKAGEBINARIES = 'http://ipws-ssota-qa.blurdev.com/package-management-1.0/ws/pm/1/binaries'
UPLOAD_CHUNKSIZE = 64 * 1024 * 1024
UPLOAD_CHUNKSIZE = 1

@profile
def _pkgtopm(someiter, ):
    pprint('Starting to upload binary to: %s' % GETPACKAGEBINARIES)
    pkgresp = requests.post(GETPACKAGEBINARIES, data=someiter)
    pprint('Finished uploading binary: {}'.format(pkgresp.text))
    pguid = pkgresp.json().get('packageid')
    requests.delete(GETPACKAGEBINARIES + '/' + pguid)

@profile
def pushfromjenkins(zipFileUrl):
    pprint(datetime.now())
    rzip = requests.get(zipFileUrl, auth=('fkr684', '91373ffe21a0d3b25b3739001a0dd68d'), stream=True)
    _pkgtopm(rzip.iter_content(chunk_size=UPLOAD_CHUNKSIZE))
    pprint(datetime.now())

if __name__ == '__main__':
    pushfromjenkins(sys.argv[1])
