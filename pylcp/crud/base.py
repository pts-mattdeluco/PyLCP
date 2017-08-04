"""Loyalty domain objects for LCP services

The domain objects derived from LCPResource can be used for basic CRUD
operations to support internal services.

"""
from future import standard_library
standard_library.install_aliases()  # NOQA

from builtins import object


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
        d = self.json
        for k in ['links', 'self', 'href']:
            d = d.get(k, None) if isinstance(d, dict) else None
        return d

    @property
    def json(self):
        return self.response.json() if self.response else {}

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

    def modify(self, path, payload):
        return self._resource_from_http('patch', path, payload)

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
