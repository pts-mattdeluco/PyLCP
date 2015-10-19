from builtins import bytes

from nose.tools import eq_
from requests import adapters, models


class MockRequestAdapter(adapters.BaseAdapter):
    """A Requests transport adapter which echos the request instead of making actual
    HTTP calls.
    """

    def __init__(self, *args, **kwargs):
        self.last_request = None
        self.last_request_kwargs = None

    def send(self, request, **kwargs):
        """Suppresses sending of the request. A default response is returned
        with status code 200, `Content-Type` and `Location` headers and a
        copy of the body from the request.
        """

        self.last_request = request
        self.last_request_kwargs = kwargs

        response = models.Response()
        response.request = request
        response.connection = self
        response.status_code = 200
        response.reason = 'OK'
        response.headers = {
            'Content-Type': 'application/json',
            'location': request.url,
        }
        if request.body is not None:
            response._content = bytes(request.body.encode('utf-8'))
        return response

    def close(self):
        pass  # no connection to close

    def assert_request_properties(self, **expected_properties):
        """Assert that the listed properties are present on the request
        object as attributes.

        :param expected_properties: The attributes to validate on the request.
        """

        for property_name, expected_value in list(expected_properties.items()):
            actual_value = getattr(self.last_request, property_name)
            message = '{} did not match. Expected: {}, actual: {}'.format(property_name, expected_value, actual_value)
            eq_(actual_value, expected_value, message)

    def assert_headers_present(self, expected_headers):
        """Assert that the listed headers are present on the request.

        :param expected_headers: A dictionary of header name/value pairs.
        """

        for header_name, expected_value in list(expected_headers.items()):
            actual_value = self.last_request.headers.get(header_name)
            message = 'Header {} did not match. Expected: {}, actual: {}'.format(
                header_name,
                expected_value,
                actual_value,
            )
            eq_(actual_value, expected_value, message)
