import copy
import decimal
import json
import logging

import requests

from pylcp.mac import generate_authorization_header_value
import pylcp.url


logger = logging.getLogger(__name__)
request_logger = logging.getLogger(__name__ + '.request')
response_logger = logging.getLogger(__name__ + '.response')


class JsonResponseWrapper(object):
    def __init__(self, response):
        self.response = response

    def json(self, **kwargs):
        kwargs.setdefault('parse_float', decimal.Decimal)
        return self.response.json(**kwargs)

    def __getattr__(self, attr):
        return getattr(self.response, attr)


def _requests_response_hook(response, *args, **kwargs):
    return JsonResponseWrapper(response)


LOG_SEPARATOR = u'------------------------------------------------------------\n'


class APILogger(object):

    REQUEST_LOG_TEMPLATE = LOG_SEPARATOR + u'%(method)s %(url)s HTTP/1.1\n%(headers)s\n\n%(body)s'
    RESPONSE_LOG_TEMPLATE = LOG_SEPARATOR + u'HTTP/1.1 %(status_code)d %(reason)s\n%(headers)s\n\n%(body)s'

    def __init__(self, request_logger, response_logger):
        self.request_logger = request_logger
        self.response_logger = response_logger

    def log_request(self, request):
        if self.request_logger.isEnabledFor(logging.DEBUG):
            self.request_logger.debug(
                self.REQUEST_LOG_TEMPLATE,
                {
                    'method': request.method,
                    'url': request.url,
                    'headers': self.format_headers(request.headers),
                    'body': self.get_masked_and_formatted_request_body(request),
                }
            )

    def log_response(self, response):
        if self.response_logger.isEnabledFor(logging.DEBUG):
            self.response_logger.debug(
                self.RESPONSE_LOG_TEMPLATE,
                {
                    'status_code': response.status_code,
                    'reason': response.reason,
                    'headers': self.format_headers(response.headers),
                    'body': self.prettify_alleged_json(response.text),
                }
            )

    def format_headers(self, headers):
        return '\n'.join('{}: {}'.format(k, v) for k, v in headers.items())

    def pretty_json_dumps(self, data):
        return json.dumps(data, sort_keys=True, indent=2)

    def prettify_alleged_json(self, text):
        try:
            return self.pretty_json_dumps(json.loads(text))
        except:
            return text

    def mask_sensitive_data(self, data):
        if not data:
            return
        if isinstance(data, basestring):
            try:
                data = json.loads(data)
            except ValueError:
                return data
            return json.dumps(self.mask_sensitive_data(data))

        copied_data = copy.deepcopy(data)
        copied_data = mask_sensitive_billing_info_data(copied_data)

        if 'password' in copied_data:
            copied_data['password'] = 'XXX'

        return copied_data

    def get_masked_and_formatted_request_body(self, request):
        """
        Prepares a request body for logging by masking sensitive fields and
        formatting json data with indentation for readability.
        """
        if request.headers.get('content-type') == 'application/json' and request.body:
            try:
                data = json.loads(request.body)
            except ValueError:
                return request.body
            masked_data = self.mask_sensitive_data(data)
            return self.pretty_json_dumps(masked_data)
        if 'charset=utf-8' in request.headers.get('content-type', ''):
            return request.body.decode('utf-8')
        return request.body


class Client(requests.Session):
    """
    A specialization of :class:`requests.Session` for making signed requests to the Points Loyalty Commerce Platform.

    :param base_url: The HTTP scheme, netloc and version prefix for the LCP.
    :param key_id: The MAC key identifier of the LCP credentials used for signing. Use `None` for anonymous requests.
    :param shared_secret: The MAC key to use to sign requests.
    """

    api_logger = APILogger(request_logger, response_logger)

    def __init__(self, base_url, key_id=None, shared_secret=None, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        if key_id is not None:
            self.auth = MACAuth(key_id, shared_secret)

        self.base_url = base_url
        self.key_id = key_id
        self.shared_secret = shared_secret
        self.hooks = {'response': _requests_response_hook}

    def prepare_request(self, request):
        if self.base_url and not request.url.startswith('http'):
            request.url = pylcp.url.url_path_join(self.base_url, request.url)

        if request.method.upper() in {'PATCH', 'POST', 'PUT'}:
            request.headers.setdefault('content-type', 'application/json')
        else:
            request.headers.setdefault('content-type', '')

        prepared_request = super(Client, self).prepare_request(request)
        return prepared_request

    def send(self, request, **kwargs):
        """Send a given :class:`requests.PreparedRequest`.

        The request and response are logged.
        """
        self._log_request(request)
        response = super(Client, self).send(request, **kwargs)
        self._log_response(response)
        return response

    def _log_request(self, request):
        self.api_logger.log_request(request)

    def _log_response(self, response):
        self.api_logger.log_response(response)


class MACAuth(requests.auth.AuthBase):
    """
    Attaches an authorization MAC header to the given request.
    """
    def __init__(self, key_id, shared_secret):
        self.key_id = key_id
        self.shared_secret = shared_secret

    def __call__(self, request):
        request.headers['Authorization'] = generate_authorization_header_value(
            request.method,
            request.url,
            self.key_id,
            self.shared_secret,
            request.headers['content-type'],
            request.body
        )
        return request


def mask_credit_card_number(credit_card_number):
    """Returns `credit_card_number` with all but the last 4 digits masked with 'X'.
    """
    if credit_card_number is None:
        return None

    credit_card_number = str(credit_card_number)
    if len(credit_card_number) < 4:
        raise ValueError("Insufficient digits in number to complete masking. At least 4 digits must be present")
    return "X" * (len(credit_card_number) - 4) + credit_card_number[-4:]


def mask_credit_card_number_with_bin(credit_card_number):
    """Returns `credit_card_number` with all but the BIN (first 6 digits) and
    the last 4 digits masked with 'X'.
    """
    if credit_card_number is None:
        return None

    credit_card_number = str(credit_card_number)
    if len(credit_card_number) < 10:
        raise ValueError("Insufficient digits in number to complete masking. At least 10 digits must be present")
    masked = 'X' * (len(credit_card_number) - 10)
    return credit_card_number[0:6] + masked + credit_card_number[-4:]


def mask_sensitive_billing_info_data(data):
    """Returns `data` with the `cardNumber` and `securityCode` fields of
    the standard LCP `billingInfo` sub-dictionary masked.
    """
    if not data:
        return
    if isinstance(data, basestring):
        try:
            data = json.loads(data)
        except ValueError:
            return data
        return json.dumps(mask_sensitive_billing_info_data(data))

    copied_data = copy.deepcopy(data)
    if 'billingInfo' in copied_data:
        if 'cardNumber' in copied_data['billingInfo']:
            card_number = copied_data['billingInfo']['cardNumber']
            copied_data['billingInfo']['cardNumber'] = mask_credit_card_number(card_number)

        if 'securityCode' in copied_data['billingInfo']:
            copied_data['billingInfo']['securityCode'] = 'XXX'
    return copied_data
