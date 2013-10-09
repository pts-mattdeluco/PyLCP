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

    def get(self, url, params=None):
        return self.request('GET', url, headers={}, params=params)

    def put(self, url, headers={}, params=None):
        return self.request('PUT', url, headers=headers, params=params)

    def delete(self, url):
        return self.request('DELETE', url, headers={})

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
            '%(method)s %(url)s HTTP/1.0\n%(headers)s\n\n%(body)s',
            {
                'method': method,
                'url': url,
                'headers': format_headers(kwargs.get('headers', {})),
                'body': prettify_alleged_json(kwargs.get('data', ''))})
        response = requests.request(method, url, **kwargs)
        response_logger.debug(
            '------------------------------------------------------------\n'
            'HTTP/1.0 %(status_code)d %(reason)s\n%(headers)s\n\n%(body)s',
            {
                'status_code': response.status_code,
                'reason': response.reason,
                'headers': format_headers(response.headers),
                'body': prettify_alleged_json(response.text)})
        return response
