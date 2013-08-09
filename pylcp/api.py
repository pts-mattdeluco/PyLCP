import logging
import json
import urlparse

import requests

from lcp.mac import generate_authorization_header_value


logger = logging.getLogger(__file__)


class Client(object):
    def __init__(self, base_url, key_id=None, shared_secret=None):
        self.key_id = key_id
        self.shared_secret = shared_secret
        self.base_url = base_url

    def post(self, url, **payload):
        return self.request('POST', url, **payload)

    def get(self, url):
        return self.request('GET', url)

    def request(self, method, url, **payload):
        headers = {'Content-Type': 'application/json'}
        if not url.startswith('http'):
            url = self.base_url + url
        logger.debug('%s to %s with %s', method, url, payload)
        body = json.dumps(payload)
        url_parts = urlparse.urlparse(url)
        if self.key_id:
            headers['Authorization'] = generate_authorization_header_value(
                method,
                url_parts.hostname,
                url_parts.port or '80',
                url_parts.path,
                self.key_id,
                self.shared_secret,
                headers['Content-Type'],
                body)

        response = requests.request(method, url, data=body, headers=headers)
        logger.debug('Got %s status code with body: \n%s', response.status_code, response.text)
        return response
