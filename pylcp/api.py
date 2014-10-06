import json
import logging
import copy

import requests


from pylcp.mac import generate_authorization_header_value
import pylcp.url


logger = logging.getLogger(__name__)
request_logger = logging.getLogger(__name__ + '.request')
response_logger = logging.getLogger(__name__ + '.response')


LOG_SEPARATOR = '------------------------------------------------------------\n'
REQUEST_LOG_TEMPLATE = LOG_SEPARATOR + '%(method)s %(url)s HTTP/1.1\n%(headers)s\n\n%(body)s'
RESPONSE_LOG_TEMPLATE = LOG_SEPARATOR + 'HTTP/1.1 %(status_code)d %(reason)s\n%(headers)s\n\n%(body)s'


class Client(requests.Session):
    """
    Client for making signed requests to the Points Loyalty Commerce Platform.
    """
    def __init__(self, base_url, key_id=None, shared_secret=None, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        if key_id is not None:
            self.auth = MACAuth(key_id, shared_secret)

        self.base_url = base_url
        self.key_id = key_id
        self.shared_secret = shared_secret

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
        self._log_request(request)
        response = super(Client, self).send(request, **kwargs)
        self._log_response(response)
        return response

    def _log_request(self, request):
        if request_logger.isEnabledFor(logging.DEBUG):
            request_logger.debug(
                REQUEST_LOG_TEMPLATE,
                {
                    'method': request.method,
                    'url': request.url,
                    'headers': format_headers(request.headers),
                    'body': get_masked_and_formatted_request_body(request),
                }
            )

    def _log_response(self, response):
        # don't bother processing if we're not going to log
        if response_logger.isEnabledFor(logging.DEBUG):
            response_logger.debug(
                RESPONSE_LOG_TEMPLATE,
                {
                    'status_code': response.status_code,
                    'reason': response.reason,
                    'headers': format_headers(response.headers),
                    'body': prettify_alleged_json(response.text),
                }
            )


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


def format_headers(headers):
    return '\n'.join(
        "{}: {}".format(k, v) for k, v in headers.items())


def pretty_json_dumps(data):
    return json.dumps(data, sort_keys=True, indent=2)


def prettify_alleged_json(text):
    try:
        return pretty_json_dumps(json.loads(text))
    except:
        return text


def mask_credit_card_number(credit_card_number):
    if credit_card_number is None:
        return None

    credit_card_number = str(credit_card_number)

    return "X" * (len(credit_card_number) - 4) + credit_card_number[-4:]


def mask_sensitive_data(data):
    if not data:
        return
    if isinstance(data, basestring):
        try:
            data = json.loads(data)
        except ValueError:
            return data
        return json.dumps(mask_sensitive_data(data))

    copied_data = copy.deepcopy(data)
    if 'billingInfo' in copied_data:
        if 'cardNumber' in copied_data['billingInfo']:
            card_number = copied_data['billingInfo']['cardNumber']
            copied_data['billingInfo']['cardNumber'] = mask_credit_card_number(card_number)

        if 'securityCode' in copied_data['billingInfo']:
            copied_data['billingInfo']['securityCode'] = 'XXX'

    if 'password' in copied_data:
        copied_data['password'] = 'XXX'

    return copied_data


def get_masked_and_formatted_request_body(request):
    """
    Prepares a request body for logging by masking sensitive fields and
    formatting json data with indentation for readability.
    """
    if request.headers.get('content-type') == 'application/json' and request.body:
        try:
            data = json.loads(request.body)
        except ValueError:
            return request.body
        masked_data = mask_sensitive_data(data)
        return pretty_json_dumps(masked_data)

    return request.body
