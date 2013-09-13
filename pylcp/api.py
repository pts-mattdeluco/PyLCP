import logging

import requests

from lcp.mac import generate_authorization_header_value


logger = logging.getLogger(__file__)


class Client(object):
    def __init__(self, base_url, key_id=None, shared_secret=None):
        self.key_id = key_id
        self.shared_secret = shared_secret
        self.base_url = base_url

    def post(self, url, **kwargs):
        kwargs.setdefault('headers', {'Content-Type': 'application/json'})
        return self.request('POST', url, **kwargs)

    def get(self, url):
        return self.request('GET', url, headers={})

    def request(self, method, url, **kwargs):
        if not url.startswith('http'):
            url = self.base_url + url
        if self.key_id:
            kwargs['headers']['Authorization'] = generate_authorization_header_value(
                method,
                url,
                self.key_id,
                self.shared_secret,
                kwargs['headers'].get('Content-Type', ''),
                kwargs.get('data', '')
            )
        logger.debug('%s to %s with %s', method, url, kwargs)
        response = requests.request(method, url, **kwargs)
        logger.debug('Got %s status code with body: \n%s', response.status_code, response.text)
        return response
