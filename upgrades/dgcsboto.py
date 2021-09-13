'''
>>> import boto
>>> from gslib.third_party.oauth2_plugin import oauth2_plugin
>>> # URI scheme for Google Cloud Storage.
... GOOGLE_STORAGE = 'gs'
>>> # URI scheme for accessing local files.
... LOCAL_FILE = 'file'
>>> uri = boto.storage_uri('', GOOGLE_STORAGE)
>>> for bucket in uri.get_all_buckets():
...     print bucket.name
... 
arjun-cloudsqltest-bucket
arjun-confcentral-acl
arjun-gcp-image-bucket
arjun-gcp-jmeter-server-package-bucket
arjun-gcp-test1
ben-confcentral-uploads
ben-confcentral-vendor1
benbongalon-dra-bucket
benbongalon-eu
benbongalon-us
com-motorola-gce-startup-packages
com-motorola-gce-startup-scripts
confcentral-milind
confcentral-milind-eu
deviceservices-jmeter
gcpexam2013bqexport
gcptrainingsept2013gcs-milind-khandekar
milindkhandekar-at-gmail
motogcedisks
mybucketgae
ota-packages
photobucket-gcp
shashibucket
suppackages
>>> uri = boto.storage_uri('ota-packages', GOOGLE_STORAGE)
>>> for obj in uri.get_bucket():
...     print '%s://%s/%s' % (uri.scheme, uri.bucket_name, obj.name)
... 
gs://ota-packages/delta-ota-Blur_Version.98.0.100-98.0.188.XT912.Verizon.en.US.zip
>>> ^D
'''

import boto
from gslib.third_party.oauth2_plugin import oauth2_plugin
GOOGLE_STORAGE = 'gs'
LOCAL_FILE = 'file'
uri = boto.storage_uri('ota-packages', GOOGLE_STORAGE)
for obj in uri.get_bucket():
    print '%s://%s/%s' % (uri.scheme, uri.bucket_name, obj.name)
    pass
