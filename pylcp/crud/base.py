"""Loyalty domain objects for LCP services

The domain objects derived from LCPResource can be used for basic CRUD
operations to support internal services.

"""
from future import standard_library
standard_library.install_aliases()  # NOQA

from builtins import object
try:
    from http.client import NO_CONTENT
except ImportError:
    from httplib import NO_CONTENT

import requests
import simplejson as json


class LCPResource(object):
    """Base class for loyalty domain objects for LCP services

    When defining new domain objects, overrides of __init__ and create must call
    the superclass implementations to ensure that the common id and url properties
    are correctly initialized.
    """
    def __init__(self, response=None):
        self.response = response

    @property
    def url(self):
        if self.response and 'location' in self.response.headers:
            return self.response.headers['location']

        # Traverse the dictionary returning None if a key isn't found during traversal
        return reduce(lambda d, key: d.get(key, None) if isinstance(d, dict) else None,
                      ['links', 'self', 'href'], self.json)

    @property
    def json(self):
        if self.response:
            return self.response.json()
        return {}

    def __getitem__(self, key):
        return self.json[key]


class LCPCrud(object):

    """Cruds are responsible for translating CRUD operations into http
    requests (method, url-path, querystring, payload) and interpreting http
    responses (success vs failure).
    :param http_client: Must be of be a subclass of requests.Session

    """

    def __init__(self, http_client):
        self.http_client = http_client

    @property
    def resource_class(self):
        return LCPResource

    def create(self, path, payload):
        return self._resource_from_http('post', path, payload)

    def read(self, path):
        return self._resource_from_http('get', path)

    def update(self, path, payload):
        return self._resource_from_http('put', path, payload)

    def delete(self, path):
        return self._resource_from_http('delete', path)

    def search(self, path, params=None):
        return self._resource_from_http('get', path, params=params)

    def _resource_from_http(self, method, path, payload=None, params=None):
        response = None

        try:
            response = self._http_method(method)(path, data=payload, params=params)
            response.raise_for_status()
        except requests.RequestException:
            raise CRUDError(path, method, response, **{'request_payload': payload, 'request_parameters': params})
        return self.resource_class(response)

    def _http_method(self, method):
        return getattr(self.http_client, method.lower())


class CRUDError(Exception):
    def __init__(self, url, method, response, **request_kwargs):
        formatted_request = self._format_optional_args(request_kwargs)

        super(CRUDError, self).__init__(
            "{status_code} returned.\n"
            "Method: {method}\n"
            "Correlation ID: {cid}\n"
            "URL: {url}\n"
            "{formatted_request}"
            "Response: {response}".format(
                url=url,
                method=method,
                status_code=response.status_code,
                cid=response.headers.get('pts-lcp-cid', 'none'),
                formatted_request=formatted_request,
                response=response.text,
            ))

    def _format_optional_args(self, request_kwargs):
        formatted_request = ''
        for key in list(request_kwargs.keys()):
            value = request_kwargs[key]
            label = self._format_label(key)

            if isinstance(value, dict):
                formatted_value = self._format_dictionary(label, value)
            else:
                formatted_value = u'{}: "{}"\n'.format(label, value)
            formatted_request += formatted_value

        return formatted_request

    def _format_label(self, text):
        return text.replace('_', ' ').capitalize()

    def _format_dictionary(self, label, dict_to_format):
        formatted_dictionary = ''
        if dict_to_format is not None:
            formatted_dictionary = u'{}: {}\n'.format(label, json.dumps(dict_to_format, indent=2, sort_keys=True))
        return formatted_dictionary
