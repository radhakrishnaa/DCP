# content of conftest.py

import pytest
from common import info


class VirtualDisplayProxy():    
    def __init__(self):
        # Import the module only if this class is instantiated; this allows the testsuite 
        #   to be run on hosts that without a virtual display server running (don't use
        #   the --usevirtualdisplay command option when you run py.test)
        import pyvirtualdisplay
        print "\n*** Starting virtual display ***\n"
        self.display = pyvirtualdisplay.Display(visible=0, size=(800, 600))
        self.display.start()
    
    def stop(self):
        print "\n*** Stopping virtual display ***\n"
        self.display.stop()


def pytest_addoption(parser):
    parser.addoption("--cloudset", action="store", help="Cloudset to run test on")
    parser.addoption("--usevirtualdisplay", action="store_true", default=False, help="Use a Virtual display")

@pytest.fixture
def cloudset(request):
    cval = request.config.getoption("--cloudset")
    if cval is None:
        pytest.exit("Cloudset is not defined")
    return cval.lower()

@pytest.fixture(scope='session', autouse=True)
def start_virtualdisplay(request):
    if request.config.getoption("--usevirtualdisplay"):
        dproxy = VirtualDisplayProxy()
        request.addfinalizer(dproxy.stop)


@pytest.fixture(scope='module')
def check_umportal():
    """Verify that OTAmatic is running before executing the testcases"""
    return  #  NOT USED
    
    try:
        print "\n\n"
        info("Checking if OTAmatic is running ok...")
        driver = UmPortal(pytest.config.getoption('cloudset'))
        #driver.login()
        #driver.doSomething()
        driver.close()
        info("Check succeeded. Life is good!")
        print "\n\n"
    except Exception, e:
        pytest.exit("Aborting all remaining tests! Upgrade Management portal is not working: %s" % e)
