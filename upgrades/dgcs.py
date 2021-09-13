#!/usr/bin/env python

import os.path

import apiclient.discovery
from apiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaIoBaseUpload
import tempfile
import httplib2
import requests
import json
import uuid
import io
import httplib
httplib.HTTPConnection.debuglevel = 0

from pprint import pprint

import logging
logger = logging.getLogger(__name__)

from oauth2client.client import SignedJwtAssertionCredentials

from django.conf import settings as djsettings
from django.core.exceptions import ImproperlyConfigured
try:
    KEYPEM = djsettings.SERVICE_ACCOUNT_PK
except ImproperlyConfigured:
    KEYPEM = '''-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDOxlzgplxAMJR+mZh7RMeoFnrWJojf/TzSUJ5E/TaieWSyh6RB
9HLRjoNwStmA7GLMQLiKoGwadxX6kQRGBwnh7mC38iqqmiB/u9QSbdadU3WNP4ma
Udqi1YhIlWj125a3GjkkHragxRWwjoZ6SfAmFHMCFhcIXkcsT0rO8G2gYQIDAQAB
AoGAEYxwMXis952n3J64fC24LCHMRwR6NVhOoyLIa955loxq6WPtotNWM0a/DPat
Qu3M7LzJbKp0wkI9EUjhbfgG9Iiw0sP+Vl9JK0wAWQ9x5JgCc9d1bY1g/TipnBJ5
lQ/O0qRcwl3t7MunNPgvLELajJvg1s9RknMv7fVEcA2ioOECQQDrEp8ROoOm9RyL
mfjOPkgezt8xd7yFEO3Ee7l9Fn84+sMWNw5HREeZXgVbN8wReCCLQzdCDtlRptzt
GQOB0mL9AkEA4S7S+QFZaZIvH9uayJtealytC+Tl3Q5xg/w7UpuTMyNXvy4Nnf31
rj+x2zSzd2VcC9Xqq+ESYsVDRP7UFOpKNQJBANXNdv29gbZdo1vZa/FxtjjHITsl
00IX1pnpihiaWJYjhUJ0SrlJAfIdELQZeLK+1qKzPNQJG2FnafL/2C/AgaUCQDKo
7h3HB+6QTLnGFhR7n8od/3BllrEcxr0CyfXTulIO6XbBTZ71u4fwHHtMZ/O8gfDH
t3vjrtc5ueCT0/LAouECQQCwAruFTukZTbGor4tkzwAIdx1pSROVtnvmq40/8oeo
h+/e+RHTCBhZG2vhWQnLJlpKclrp7GhkDgomg++6IxXl
-----END RSA PRIVATE KEY-----
'''

BUCKET = 'com-motorola-cds-otapackages'
SERVICE_ACCOUNT = '523753976398-pbolclbq5n6i5na989svg6g5loor5fnr@developer.gserviceaccount.com'
BUCKET_ACCESS = 'https://www.googleapis.com/auth/devstorage.full_control'

# Retry transport and file IO errors.
RETRYABLE_ERRORS = (httplib2.HttpLib2Error, IOError)

# Number of times to retry failed downloads.
NUM_RETRIES = 5

# Number of bytes to send/receive in each request.
CHUNKSIZE = 2 * 1024 * 1024

# Mimetype to use if one can't be guessed from the file extension.
DEFAULT_MIMETYPE = 'application/octet-stream'

def oauth2gcsaccess():
    logger.debug('Setting up credentials...')
    return SignedJwtAssertionCredentials(SERVICE_ACCOUNT, KEYPEM, BUCKET_ACCESS)

def getGcsClient(credentials):
    logger.debug('Building GCS API client using OAuth2.0 credentials...')
    # Set up http with the credentials.
    authorized_http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('storage', 'v1beta2', http=authorized_http)
    return service

def upload(filename, fileobj, service = None):
    logger.debug('Building GCS upload request...')
    if not service:
        '''
        Each time, I take a hit on doing the two-legged OAuth2.0 dance
        This is slow, but how often do we upload a package?
        If this is indeed slow, get a refresh_token and reuse to get access token.
        '''
        service = getGcsClient(oauth2gcsaccess())
        pass
    # make a random UUID
    s = uuid.uuid4()
    packageguid = s.urn.split(':')[-1]
    gsobjectname = '%s.%s' % (os.path.split(filename)[-1], packageguid)
    media = MediaIoBaseUpload(fileobj, DEFAULT_MIMETYPE, chunksize=CHUNKSIZE, resumable=True)
    
    request = service.objects().insert(bucket=BUCKET, name=gsobjectname,
                                       media_body=media)
    logger.info('Uploading file: %s to bucket: %s object: %s ' % (filename, BUCKET,
                                                            gsobjectname))

    progressless_iters = 0
    response = None
    while response is None:
        error = None
        try:
            progress, response = request.next_chunk()
            if progress:
                logger.debug('Upload %d%%' % (100 * progress.progress()))
        except HttpError, err:
            error = err
            if err.resp.status < 500:
                raise Exception('%s' % str(err))
        except RETRYABLE_ERRORS, err:
            error = err

        if error:
            progressless_iters += 1
            handle_progressless_iter(error, progressless_iters)
        else:
            progressless_iters = 0

    logger.info( '\nUpload complete!' )

    if logger.isEnabledFor('DEBUG'):
        logger.debug('Uploaded Object:')
        pprint(response)
        pass

    # return the name and size
    return (response['name'], response['size'])

def delete(gsobjectname, service = None):
    logger.debug('Building GCS delete request...')
    if not service:
        '''
        Each time, I take a hit on doing the two-legged OAuth2.0 dance
        This is slow, but how often do we upload a package?
        If this is indeed slow, get a refresh_token and reuse to get access token.
        '''
        service = getGcsClient(oauth2gcsaccess())
        pass
    logger.info('Deleting object from bucket: %s object: %s ' % (BUCKET, gsobjectname))
    resp = service.objects().delete(bucket=BUCKET, object=gsobjectname,).execute()
    logger.info('Deleted')
    return resp

def download(bucket_name, object_name, service = None):
    logger.debug('Building GCS upload request...')
    if not service:
        '''
        Each time, I take a hit on doing the two-legged OAuth2.0 dance
        This is slow, but how often do we upload a package?
        If this is indeed slow, get a refresh_token and reuse to get access token.
        '''
        service = getGcsClient(oauth2gcsaccess())
        pass
    bucket_name, object_name = ('ota-packages', 'delta-ota-Blur_Version.98.0.100-98.0.188.XT912.Verizon.en.US.zip')

    print 'Building download request...'
    with tempfile.NamedTemporaryFile() as f:
        request = service.objects().get_media(bucket=bucket_name, object=object_name)
        media = MediaIoBaseDownload(f, request, chunksize=CHUNKSIZE)

        print 'Downloading bucket: %s object: %s to file: %s' % (bucket_name,
                                                                 object_name,
                                                                 f.name)

        progressless_iters = 0
        done = False
        while not done:
            error = None
            try:
                progress, done = media.next_chunk()
                if progress:
                    pprint('Download %d%%.' % int(progress.progress() * 100),)
            except HttpError, err:
                error = err
                if err.resp.status < 500:
                    raise
            except RETRYABLE_ERRORS, err:
                error = err

            if error:
                progressless_iters += 1
                handle_progressless_iter(error, progressless_iters)
            else:
                progressless_iters = 0

        print '\nDownload complete!'

def handle_progressless_iter(error, progressless_iters):
    if progressless_iters > NUM_RETRIES:
        raise Exception('Failed to make upload progress to GCS for too many consecutive iterations.  Giving up')

    sleeptime = random.random() * (2**progressless_iters)
    logger.warn('Caught exception (%s). Sleeping for %s seconds before retry #%d.'
                % (str(error), sleeptime, progressless_iters))
    time.sleep(sleeptime)

def setup_service():
    credentials = oauth2gcsaccess()
    print 'Credentials prepared.'
    storage = getGcsClient(credentials)
    pprint(storage)
    return storage

def uploadlargewrapper(jenkinsurl, authtuple, service = None):
    r = getbinary(jenkinsurl, authtuple)
    upload('testname', io.BytesIO(r.iter_content()), service)

def getbinary(jenkinsurl, authtuple):
    return requests.get(jenkinsurl, auth=authtuple, stream=True)

def getheaders():
    creds = oauth2gcsaccess()
    # Does creds have a valid access token?
    if not creds.access_token:
        # Fake a refresh call on a bogus Http object
        creds._refresh(httplib2.Http().request)
        pass

    # Now creds has valid access token, so get a HTTP header:
    headers = {}
    creds.apply(headers)
    pprint(headers)
    return headers

def rawupload(jenkinsurl, authtuple):
    r = getbinary(jenkinsurl, authtuple)
    headers = getheaders()
    # http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification
    requests.post('https://www.googleapis.com/upload/storage/v1beta2/b/com-motorola-cds-otapackages/o?uploadType=media&name=test2',
                  headers = headers,
                  data = r.iter_content(chunk_size=CHUNKSIZE),
                  )

def postupload(filename, datastream):
    headers = getheaders()
    # http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification
    r = requests.post('https://www.googleapis.com/upload/storage/v1beta2/b/{bucket}/o?uploadType=media&name={filename}'.format(bucket=BUCKET, filename=filename),
                  headers = headers,
                  data = datastream,
                  )
    return r

def getGcsClient(credentials):
    logger.debug('Building GCS API client using OAuth2.0 credentials...')
    # Set up http with the credentials.
    authorized_http = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('storage', 'v1beta2', http=authorized_http)
    return service
    
def main():
    storage = setup_service()
    FIELDS = 'items(name)'
    list_response = storage.objects().list(bucket=BUCKET,
                                           fields=FIELDS).execute()
    pprint(list_response)
    download(bucket_name=BUCKET, object_name = list_response['items'][0], service = storage)
    import sys
    from datetime import datetime
    upload('/tmp/delta-ota-Blur_Version.14.0.539-14.0.548.falcon_umtsds.Brasil.en.BR.zip', 'delta-ota-Blur_Version.14.0.539-14.0.548.falcon_umtsds.Brasil.en.BR.zip.%s' % repr(datetime.now()), storage)
    return

if __name__ == '__main__':
    main()
    pass
