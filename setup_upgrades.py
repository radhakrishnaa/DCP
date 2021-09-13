from setuptools import setup, find_packages
import os, sys
from datetime import datetime

setup(
    name='MotorolaPortal',
    version='0.0.5',
    author='OTA Team, Cloud Services',
    author_email='suteam@motorola.com',
    url='https://sites.google.com/a/motorola.com/software-updates/',
    packages= find_packages('.', exclude=('dcp',)),
    description='Motorola Portal',
    install_requires=[
        "distribute==0.6.49",
        "Django==1.5.1",
        "South==0.7.6",
        "MySQL_python==1.2.4",
        "django_filter==0.6",
        "django_reversion==1.7",
        "requests==2.0.1",
        "pycrypto==2.6",
        "oauth2client==1.2",
        "google-api-python-client==1.2",
        ],
        include_package_data=True,
        zip_safe=False,
    )
