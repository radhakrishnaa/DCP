# Standard library imports
from time import sleep

# Third-party imports
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait

# Local imports
from common import *


DEFAULT_TIMEOUT_SECS = 60

SUP_URL = {
    'QA300': 'http://icws-ssota-qa.blurdev.com',
    'SDC200': 'http://upportal-sdc200.blurdev.com'
}

DEFAULT_LOGIN = {
    'email' : 'userotatest001@gmail.com',
    'passwd' : 'm0t0bl6r8We'
}


class SUPDriver():
    def __init__(self, cloudset):
        self.browser = webdriver.Chrome()
        self.cloudset = cloudset.upper()

    def goto(self, tabName):
        """Go to the specified SUP tab (menu)"""
        tabLinks = {
            'upgrades' : '/upgrades#/paths',
            'settings' : '/upgrades#/settings',   # LINK NOT ACTIVE
            'upgrade logs' : '/upgrades#/events',
            'device info' : '/upgrades#/deviceinfo',
            'map reports' : '/upgrades#/mapreports',
            'lists' : '/upgrades#/lists',
            'admin' : '/upgrades#/admin'
        }
        self.browser.get(SUP_URL[self.cloudset] + tabLinks[tabName.lower()])

    def login(self, creds=DEFAULT_LOGIN):
        """Login to SUP"""
        # @TODO detect if already logged in and skip
        browser = self.browser
        browser.get(SUP_URL[self.cloudset])
        el = WebDriverWait(browser, DEFAULT_TIMEOUT_SECS).until(lambda x: x.find_element_by_id('Email'))
        el.send_keys(creds['email'])
        el2 = WebDriverWait(browser, DEFAULT_TIMEOUT_SECS).until(lambda x: x.find_element_by_id('Passwd'))
        el2.send_keys(creds['passwd'])
        btn = WebDriverWait(browser, DEFAULT_TIMEOUT_SECS).until(lambda x: x.find_element_by_id('signIn'))
        btn.click()
    
        # Detect "web page not available" error doe to CAS issue
        WebDriverWait(browser, DEFAULT_TIMEOUT_SECS).until(lambda x: x.title.startswith('https'))
        el = browser.find_element_by_tag_name('h1')
    
        # Do the CAS workaround thing... replace the https URL with http twice
        url = browser.title.replace('https:','http:', 1).replace(' is not available','')
        browser.get(url)
        url2 = browser.title.replace('https:','http:', 1).replace(' is not available','')
        browser.get(url2)

    def get_paths(self):
        """Go to the Upgrades page and return the list of upgrade paths"""
        self.goto('Upgrades')
        paths = []
        tableRows = WebDriverWait(self.browser, DEFAULT_TIMEOUT_SECS).until(lambda x: x.find_elements_by_xpath("//tr[@class='ng-scope']"))
        for row in tableRows:
            paths.append( [col.text for col in row.find_elements_by_tag_name('td')] )
        return paths

    def get_device_lists(self):
        """Go to the List page and return the list of Device Lists (aka target lists)"""
        # @TODO figure out a way to get the Device List without waiting for the size value
        #       to be completely rendered (this takes a LONG time)
        self.goto('Lists')
        lists = []
        ###  This is tricky to implement because the DOM structure is messy
        ###  @TODO Ask dev to add element IDs to simplify scraping the data!
        return lists

    def close(self):
        self.browser.close()