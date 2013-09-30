import json
import logging

import requests

from lcp.mac import generate_authorization_header_value


logger = logging.getLogger(__name__)
request_logger = logging.getLogger(__name__ + '.request')
response_logger = logging.getLogger(__name__ + '.response')


def format_headers(headers):
    return '\n'.join(
        "{}: {}".format(k, v) for k, v in headers.items())


def prettify_alleged_json(text):
    try:
        return json.dumps(json.loads(text), sort_keys=True, indent=2)
    except:
        return text


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
            kwargs['headers']['Authorization'] = \
                generate_authorization_header_value(
                    method,
                    url,
                    self.key_id,
                    self.shared_secret,
                    kwargs['headers'].get('Content-Type', ''),
                    kwargs.get('data', '')
                )
        request_logger.debug(
            '------------------------------------------------------------\n'
            '%s %s HTTP/1.0\n%s\n\n%s',
            method, url,
            format_headers(kwargs.get('headers', {})),
            prettify_alleged_json(kwargs.get('data', '')))
        response = requests.request(method, url, **kwargs)
        response_logger.debug(
            '------------------------------------------------------------\n'
            'HTTP/1.0 %d %s\n%s\n\n%s',
            response.status_code, response.reason,
            format_headers(response.headers),
            prettify_alleged_json(response.text))
        return response
