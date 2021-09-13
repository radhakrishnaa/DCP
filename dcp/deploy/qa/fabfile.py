from fabric.api import run, sudo, env, cd
from fabric.operations import put
from fabric.contrib import files
from fabric.context_managers import shell_env

PACKAGE_NAME = 'gdicfg-1.12.2'

# env.hosts = ['ws001-dcp-sdc200.ilc.blurdev.com']
env.hosts = ['ws001-dcp-qa300.ilc.blurdev.com']
# env.hosts = ['172.22.4.43']
# env.hosts = ['172.22.4.44']
# env.hosts = ['172.24.4.43']
# env.hosts = ['172.24.4.44']


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

        sudo('ln -s settings_dev.py gdicfg/dcp/local_settings.conf')

        # use sitepackages containing python modules from a different location
        # than the python default sitepackages as that is already installed
        with shell_env(PYTHONPATH='/home/apache/.local/lib/python2.7/site-packages/'):
            sudo('/opt/python2.7/bin/python /home/apache/gdicfg/manage.py migrate api')

        sudo('chown -R apache:apache gdicfg')
        # sudo('/etc/init.d/httpd restart')
        sudo('systemctl restart httpd')


def copybuilttoremote(local_path=None, remote_path='/home/apache'):
    if local_path is None:
        local_path = 'dist/%s.tar.gz' % PACKAGE_NAME
    put(local_path, remote_path, use_sudo=True)


def uptime():
    run("uptime")
