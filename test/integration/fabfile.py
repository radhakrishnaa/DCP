
import fabric
import getpass
import os
from fabric.api import run, sudo, env, local, cd, lcd, put

env.user = getpass.getuser()
env.hosts = ['qabuild01.qa.blurdev.com']

# Folder in remote host where the test automation scripts will be copied to
TESTROOT = '/home/tomcat/jenkins/jobs/Test_SUP_API/workspace'

# Local folder containing the cceclient tool
# Change this value according to your setup.
CCECLIENT_PATH = '../../../../dilbert/infrastructure/public/tools/cceclient'

def list():
    """Show all files/folders in the workspace where the job is deployed"""
    run('ls -lt %s' % TESTROOT)

def clean():
    """Clean up your local folder in preparation for zipping up the source tree"""
    local("rm -f *.pyc .DS_Store *Blur_Version*.zip")
    local("rm -f Test*/*.pyc Test*/.DS_Store")
    local("rm -rf Test*/__pycache__")

def copy_cceclient():
    """Copies the latest cceclient into the working folder (needed by automation)"""
    if os.path.isdir(CCECLIENT_PATH):
        local("cp -p %s/cceclient.py ." % CCECLIENT_PATH)
        local("cp -p %s/default_params_cce.txt ." % CCECLIENT_PATH)
        return True
    else:
        print "\n  ***** WARNING ******\n\nFolder '%s' was not found!" % CCECLIENT_PATH
        return False      
       
def zip():
    """Package the source tree"""
    clean()
    if not copy_cceclient():
        print "\nMake sure the latest version of 'cceclient.py' and its config file " \
            "'default_params_cce.txt' is in this folder before running 'fab zip'. " \
            "If not, copy them and run 'fab zip' again."
    with lcd(".."):
        local("tar cvfz integration.tgz integration/")

def deploy():
    """Install the package on the build server and deploy"""
    zipfile = "%s/integration.tgz" % TESTROOT
    with cd(TESTROOT):
        sudo('rm -rf integration.LAST')
        if fabric.contrib.files.exists('integration'):
            sudo('mv integration integration.LAST')
        put('../integration.tgz', zipfile, use_sudo=True)
        sudo('tar xvfz %s' % zipfile)
        sudo('chown -R tentakel:tentakel %s integration/' % zipfile)
        run('ls -lt .')
    
    
