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


class LCPResource(object):
    """Base class for loyalty domain objects for LCP services

    When defining new domain objects, overrides of __init__ and create must call
    the superclass implementations to ensure that the common id and url properties
    are correctly initialized.
    """
    def __init__(self, response=None):
        self._json = None
        self.response = response
        self._url = None

        if response is not None:
            if response.status_code != NO_CONTENT:
                self._json = response.json()
                try:
                    self._url = self._self_link()
                except KeyError:
                    pass
            if 'location' in response.headers:
                self._url = response.headers['location']

    @property
    def url(self):
        return self._url

    @property
    def json(self):
        return self.response.json()

    def _self_link(self):
        return self._json['links']['self']['href']

    def __getitem__(self, key):
        return self._json[key]


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

        response = self._http_method(method)(path, data=payload, params=params)
        response.raise_for_status()

        return self.resource_class(response)

    def _http_method(self, method):
        return getattr(self.http_client, method.lower())
