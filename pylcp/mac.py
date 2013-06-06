import requests
from urlparse import urlparse


def generate_authorization_header_value(
        http_method,
        host,
        port,
        request_path,
        mac_key_identifier,
        mac_key,
        content_type,
        body):

    return "NOT IMPLEMENTED"


def request(method, url, **kwargs):

    if 'mac_key_identifier' in kwargs and 'mac_key' in kwargs:
        parsed_url = urlparse(url)
        auth_header = generate_authorization_header_value(method,
                                                          parsed_url.hostname,
                                                          parsed_url.port,
                                                          parsed_url.path,
                                                          kwargs['mac_key_identifier'],
                                                          kwargs['mac_key'],
                                                          kwargs.get('headers')['Content-Type'],
                                                          kwargs.get('data')
                                                          )
        kwargs['headers']['Authorization'] = auth_header

    return requests.request(method, url, **kwargs)


def delete(url, **kwargs):
    return request('DELETE', url, **kwargs)


def get(url, **kwargs):
    return request('GET', url, **kwargs)


def head(url, **kwargs):
    return request('HEAD', url, **kwargs)


def patch(url, **kwargs):
    return request('PATCH', url, **kwargs)


def post(url, **kwargs):
    return request('POST', url, **kwargs)


def put(url, **kwargs):
    return request('PUT', url, **kwargs)
