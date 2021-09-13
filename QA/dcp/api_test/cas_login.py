import mechanize
import cookielib
import getpass
import sys
import os
import re

AUTH_PATH = '.auth/'

try:
    url = sys.argv[1]
except IndexError:
    print '[ERROR] Please provide test server URL'

# check user input
m = re.match(r'^([a-z]*://)([^/:]+(:\d+)?)(/[^:]*)?$', url.lower())
if not m:
    print 'Invalid server URL: %s' % url
    sys.exit(1)

url = m.group(1) + m.group(2)
hostname = m.group(2)

default_username = getpass.getuser() + '@motorola.com'
username = raw_input('email [%s]: ' % default_username) or default_username
password = getpass.getpass()

# initialize browser
cookie_jar = cookielib.MozillaCookieJar()
browser = mechanize.Browser()
browser.set_handle_robots(False)
browser.set_cookiejar(cookie_jar)

# submit user credentials
browser.open(url)
browser.select_form(nr=1)
browser['username'] = username
browser['password'] = password
res = browser.submit()

# check results and write cookies
if not os.path.exists(AUTH_PATH):
    os.makedirs(AUTH_PATH)

content = res.read()
with open(AUTH_PATH + 'result.html', 'w') as f:
    f.write(content)

if res.geturl().startswith(url):
    print 'success'
    cookie_jar.save(AUTH_PATH + 'cookies_%s.txt' % hostname)
else:
    m = re.search('<div[^>]*id="signin_err_div"[^>]*>([^<]*)</div>', content)
    print m.group(1) if m else 'unknown error'
