import os.path

# The email address for your GCS service account being used for signatures.
SERVICE_ACCOUNT_EMAIL = ('523753976398-pbolclbq5n6i5na989svg6g5loor5fnr@developer.gserviceaccount.com')

# Bucket name to use for writing example file.
BUCKET_NAME = 'com-motorola-cds-otapackages'
# Object name to use for writing example file.
OBJECT_NAME = 'junk-delta-ota-Blur_Version.129.0.3493-129.0.3519.XT907.Verizon.en.US.zip.1c78148c-63e6-49c9-94cf-c83a7d98acf'

# Set this to the path of your service account private key file, in DER format.
#
# PyCrypto requires using the DER key format, but GCS provides key files in
# pkcs12 format. To convert between formats, you can use the provided commands
# below.
#
# Given a GCS key in pkcs12 format, convert it to PEM using this command:
#   openssl pkcs12 -in path/to/key.p12 -nodes -nocerts > path/to/key.pem
# Given a GCS key in PEM format, convert it to DER format using this command:
#   openssl rsa -in privatekey.pem -inform PEM -out privatekey.der -outform DER
PRIVATE_KEY_PATH = os.path.join(os.path.dirname(__file__), 'privatekey.der')
