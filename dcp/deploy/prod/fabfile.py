from fabric.api import run, sudo, env, cd, local
from fabric.decorators import runs_once
from fabric.operations import put
from fabric.contrib import files
from fabric.context_managers import shell_env

PACKAGE_NAME = 'gdicfg-1.11'

env.hosts = [
    'ws001-dcp.va3.svcmot.com', 'ws002-dcp.va3.svcmot.com',
    'ws001-dcp.ilc.svcmot.com', 'ws002-dcp.ilc.svcmot.com',
]


def deploy():
    """Install the package on the build server and deploy"""

    with cd('/home/apache/'):
        # if gdicfg_old already exists then rename it
        if files.exists('gdicfg_old', use_sudo=True):
            sudo('rm -rf gdicfg_old')
        if files.exists('gdicfg', use_sudo=True):
            sudo('mv gdicfg gdicfg_old')

        sudo('tar -zxvf %s.tar.gz' % PACKAGE_NAME)
        sudo('mv %s gdicfg' % PACKAGE_NAME)
        sudo('mkdir gdicfg/dcp/logs')

        if files.exists('gdicfg/dcp/local_settings.conf', use_sudo=True):
            sudo('rm gdicfg/dcp/local_settings.conf')

        sudo('ln -s settings_prod.py gdicfg/dcp/local_settings.conf')

        # use sitepackages containing python modules from a different location
        # than the python default sitepackages as that is already installed
        with shell_env(PYTHONPATH='/home/apache/.local/lib/python2.7/site-packages/'):
            sudo('/opt/python2.7/bin/python /home/apache/gdicfg/manage.py migrate api')

        sudo('chown -R apache:apache gdicfg')
        sudo('/etc/init.d/httpd restart')


def copybuilttoremote(local_path=None, remote_path='/home/apache'):
    if local_path is None:
        local_path = 'dist/%s.tar.gz' % PACKAGE_NAME
    put(local_path, remote_path, use_sudo=True)


@runs_once
def pack():
    local('rm -f dist/%s.zip' % PACKAGE_NAME)
    local('zip -j dist/%s.zip dist/%s.tar.gz dcp/deploy/prod/fabfile.py' % (PACKAGE_NAME, PACKAGE_NAME))


def uptime():
    run("uptime")
