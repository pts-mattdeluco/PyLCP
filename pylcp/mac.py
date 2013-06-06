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


def delete(url, **kwargs):

    parsed_url = urlparse(url)
    auth_header = generate_authorization_header_value('DELETE',
                                                      parsed_url.hostname,
                                                      parsed_url.port,
                                                      parsed_url.path,
                                                      kwargs['mac_key_identifier'],
                                                      kwargs['mac_key'],
                                                      kwargs['headers']['Content-Type'],
                                                      kwargs['data']
                                                      )

    kwargs['headers']['Authorization'] = auth_header
    return requests.delete(url, **kwargs)


def get(url, **kwargs):
    parsed_url = urlparse(url)
    auth_header = generate_authorization_header_value('GET',
                                                      parsed_url.hostname,
                                                      parsed_url.port,
                                                      parsed_url.path,
                                                      kwargs['mac_key_identifier'],
                                                      kwargs['mac_key'],
                                                      kwargs['headers']['Content-Type'],
                                                      kwargs['data']
                                                      )

    kwargs['headers']['Authorization'] = auth_header
    return requests.delete(url, **kwargs)


def head(url, **kwargs):
    parsed_url = urlparse(url)
    auth_header = generate_authorization_header_value('HEAD',
                                                      parsed_url.hostname,
                                                      parsed_url.port,
                                                      parsed_url.path,
                                                      kwargs['mac_key_identifier'],
                                                      kwargs['mac_key'],
                                                      kwargs['headers']['Content-Type'],
                                                      kwargs['data']
                                                      )

    kwargs['headers']['Authorization'] = auth_header
    return requests.delete(url, **kwargs)


def patch(url, **kwargs):
    parsed_url = urlparse(url)
    auth_header = generate_authorization_header_value('PATCH',
                                                      parsed_url.hostname,
                                                      parsed_url.port,
                                                      parsed_url.path,
                                                      kwargs['mac_key_identifier'],
                                                      kwargs['mac_key'],
                                                      kwargs['headers']['Content-Type'],
                                                      kwargs['data']
                                                      )

    kwargs['headers']['Authorization'] = auth_header
    return requests.delete(url, **kwargs)


def post(url, **kwargs):
    parsed_url = urlparse(url)
    auth_header = generate_authorization_header_value('POST',
                                                      parsed_url.hostname,
                                                      parsed_url.port,
                                                      parsed_url.path,
                                                      kwargs['mac_key_identifier'],
                                                      kwargs['mac_key'],
                                                      kwargs['headers']['Content-Type'],
                                                      kwargs['data']
                                                      )

    kwargs['headers']['Authorization'] = auth_header
    return requests.delete(url, **kwargs)


def put(url, **kwargs):
    parsed_url = urlparse(url)
    auth_header = generate_authorization_header_value('PUT',
                                                      parsed_url.hostname,
                                                      parsed_url.port,
                                                      parsed_url.path,
                                                      kwargs['mac_key_identifier'],
                                                      kwargs['mac_key'],
                                                      kwargs['headers']['Content-Type'],
                                                      kwargs['data']
                                                      )

    kwargs['headers']['Authorization'] = auth_header
    return requests.delete(url, **kwargs)
