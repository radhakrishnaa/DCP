#!/usr/bin/python
# Author: Milind Khandekar <milind.khandekar@motorola.com>

__docformat__ = 'restructuredtext'

from fabric.api import *
import fabric.contrib.files as fab_files
from fabric.operations import put as fab_put
from fabric.network import normalize as fab_normalize
import optparse, logging, sys, os, re, csv, pprint, socket, paramiko
from datetime import datetime
from operator import itemgetter
import requests

BASEURL = 'http://jenkins-srv02.am.mot-mobility.com:8080/hudson/job/sustaining-tools_kirk_continuous/'

"""
-----------------------  Some load balancer commands
"""
@task
def deploy(remote_path, settingsfile):
    """
    Deploy build to implicit host

    """

    sudo("pip install --upgrade {remote_path}".format(**locals()), shell=False)
    sudo("/usr/local/bin/django-admin.py migrate upgrades --settings={settingsfile}".format(**locals()), shell=False)
    pass

@task
@runs_once
def copybuildtolocal(buildfileurl, user, password, local_path):
    """
    Download build artifact to local_path

    """
    r = requests.get(buildfileurl, auth=(user, password), stream=True)
    with open(local_path, 'wb') as fd:
        for chunk in r.iter_content(1024):
            fd.write(chunk)
            pass
        pass
    

@task
def copybuilttoremote(local_path, remote_path):
    """
    Copy build artifact to machine to be deployed

    """
    fab_put(local_path, remote_path, use_sudo=True, mirror_local_mode=False, mode=None)
    pass
