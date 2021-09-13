import cookielib
import logging
import os
import urllib
import urllib2

import pytest
import re
import json

# prepares logging
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """
    Adds special options to py.test call.

    :param parser: py.test options parser
    """
    parser.addoption('--hostname', action='store', default=None,
                     help='specify IP or hostname of test host')
    parser.addoption('--no-publish', action='store_true',
                     help="don't execute tests that need publish enabled")


@pytest.fixture
def server(request):
    """
    Returns DCP server wrapper instance.

    :param request: py.test request object
    """
    # parses input hostname
    value = request.config.getoption('hostname')
    if not value:
        pytest.fail('No hostname defined')
    m = re.match(r'^([a-z]*://)?([^/:]+(:\d+)?)(/[^:]*)?$', value.lower())
    if not m:
        pytest.fail('Invalid hostname defined: ' + repr(value))
    protocol = m.group(1) if m.group(1) else 'http://'
    hostname = m.group(2)
    return Server(protocol, hostname)


class Server(object):
    """DCP server wrapper."""

    def __init__(self, protocol, hostname):
        """
        Initializes DCP server wrapper.

        :param protocol: protocol used to connect to host, including "://"
        :param hostname: hostname to connect
        """
        cookie_file = '.auth/cookies_%s.txt' % hostname
        if not os.path.exists(cookie_file):
            raise NotLoggedException(protocol + hostname)
        self.protocol = protocol
        self.hostname = hostname
        cookie_jar = cookielib.MozillaCookieJar()
        cookie_jar.load(cookie_file)
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(cookie_jar))

    def request(self, path, query=None, method='GET', body=None, headers=None,
                post=None):
        """
        Makes basic HTTP request to host.

        :param path: url path
        :param query: dictionary to be encoded as query param
        :param method: http method (GET, POST, PUT, etc.)
        :param body: contents for http body
        :param headers: dictionary to be added as http headers
        :param post: dictionary to be posted as form-urlencoded. If used, will
            override method and body params
        :return: returns dictionary with following keys:
            url: opened url
            code: http return code
            headers: dictionary with returned headers
            content: returned contents as text
        """
        assert path.startswith('/')
        url = self.protocol + self.hostname + path
        if query:
            url += '?' + urllib.urlencode(query)
        req_headers = headers.copy() if headers else {}
        if post is not None:
            method = 'POST'
            body = json.dumps(post)
            req_headers['Content-type'] = 'application/json;charset=UTF-8'
        logger.info('URL Request: %s %s', method, url)

        request = urllib2.Request(url, data=body, headers=req_headers)
        request.get_method = lambda: method

        conn = self.opener.open(request)
        ret_url = conn.geturl()
        if '/ssoauth/login' in ret_url:
            raise NotLoggedException(self.protocol + self.hostname)

        return {
            'url': ret_url,
            'code': conn.getcode(),
            'headers': conn.info().dict,
            'content': conn.read(),
        }

    def api(self, method, api_name, args=None):
        """
        Makes a simple API call.

        :param method: HTTP method to be used: GET, POST, DELETE, etc.
        :param api_name: DCP api name
        :param args: dictionary storing arguments to API call
        :return:
        """
        assert not api_name.startswith('/')
        assert args is None or isinstance(args, dict)
        query = {'format': 'json'}
        headers = {}
        body = None
        if method in ('POST', 'PUT'):
            body = json.dumps(args)
            headers['Content-type'] = 'application/json;charset=UTF-8'
        elif args:
            query.update(args)
        r = self.request('/api/' + api_name, query, method,
                         headers=headers, body=body)
        if not r['content']:
            if r['code'] in (200,204):
                return None
            else:
                raise Exception('Request error %d' % r['code'])
        try:
            return json.loads(r['content'])
        except ValueError:
            raise Exception('Invalid returned content: %s' % r['content'])


class NotLoggedException(Exception):

    def __init__(self, hostname):
        super(NotLoggedException, self).__init__(
            'Domain not authenticated. Run: python cas_login.py %s' % hostname)
