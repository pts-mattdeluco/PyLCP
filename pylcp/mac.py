import base64
import hashlib
import hmac
import httplib
import logging
import os
import re
import time
import urlparse


logger = logging.getLogger(__name__)


def generate_ext(content_type, body):
    """Returns an `ext` value as described in
    `<http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.1>`_.

    :param content_type: The content type of the request e.g. application/json.'
    :param body: The request body as a byte or Unicode string.
    """
    if (
            content_type is not None and
            body is not None and
            len(content_type) > 0 and
            len(body) > 0):
        # Hashing requires a bytestring, so we need to encode back to utf-8
        # in case the body/header have already been decoded to unicode (by the
        # python json module for instance)
        if isinstance(body, unicode):
            body = body.encode('utf-8')
        if isinstance(content_type, unicode):
            content_type = content_type.encode('utf-8')
        content_type_plus_body = content_type + body
        content_type_plus_body_hash = hashlib.sha1(content_type_plus_body)
        ext = content_type_plus_body_hash.hexdigest()
    else:
        ext = ""
    return ext


def build_normalized_request_string(
        ts, nonce, http_method, host, port, request_path, ext):
    """Returns a normalized request string as described in
    `<http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.2.1>`_.

    :param ts: The integer portion of a Unix epoch timestamp.
    :param nonce: A cryptographic nonce value.
    :param http_method: The HTTP method of the request e.g. `POST`.
    :param host: The host name of the server.
    :param port: The port of the server.
    :param request_path: The path portion of the request URL i.e. everything after the host and port.
    :param ext: An ext value computed from the request content type and body.
    """

    normalized_request_string = \
        ts + '\n' + \
        nonce + '\n' + \
        http_method + '\n' + \
        request_path + '\n' + \
        host + '\n' + \
        str(port) + '\n' + \
        ext + '\n'
    return normalized_request_string


def generate_nonce():
    """Returns a random string intend for use as a nonce when computing an
    HMAC.
    """
    return base64.b64encode(os.urandom(8))


def generate_signature(mac_key, normalized_request_string):
    """Returns a request's signature given a normalized request string (a.k.a.
    a summary of the key elements of the request) and the MAC key (shared
    secret).

    The `mac_key` must match the key ID used to create the normalized request string.
    The `normalized_request_string` should be generated using
    :py:func:`build_normalized_request_string <pylcp.mac.build_normalized_request_string>`.

    :param mac_key: The MAC key to use to sign the request.
    :param normalized_request_string: Key elements of the request in a normalized form.
    """

    key = base64.b64decode(mac_key.replace('-', '+').replace('_', '/') + '=')
    signature = hmac.new(key, normalized_request_string, hashlib.sha1)
    return base64.b64encode(signature.digest())


def generate_authorization_header_value(
        http_method,
        url,
        mac_key_identifier,
        mac_key,
        content_type,
        body):
    """Returns a suitable value for the HTTP `Authorization` header that
    contains a valid signature for the request.

    :param http_method: The HTTP method of the request e.g. `POST`.
    :param url: The full URL of the request.
    :param mac_key_identifier: The ID of the MAC key to be used to sign the request
    :param mac_key: The MAC key to be used to sign the request
    :param content_type: The request content type.
    :param body: The request body as a byte or Unicde string.
    """
    url_parts = urlparse.urlparse(url)
    port = url_parts.port
    if not port:
        if url_parts.scheme == 'https':
            port = str(httplib.HTTPS_PORT)
        else:
            port = str(httplib.HTTP_PORT)
    ts = str(int(time.time()))
    nonce = generate_nonce()
    ext = generate_ext(content_type, body)
    normalized_request_string = build_normalized_request_string(
        ts,
        nonce,
        http_method,
        url_parts.hostname,
        port,
        url_parts.path,
        ext)

    signature = generate_signature(mac_key, normalized_request_string)

    return 'MAC id="%s", ts="%s", nonce="%s", ext="%s", mac="%s"' % (
        mac_key_identifier,
        ts,
        nonce,
        ext,
        signature)


class AuthHeaderValue(object):
    """As per http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02 create
    the value for the HTTP Authorization header using an existing HMAC.
    """

    auth_header_re = re.compile(
        '^\s*'
        'MAC\s+'
        'id\s*=\s*"(?P<mac_key_identifier>[^"]+)"\s*\,\s*'
        'ts\s*=\s*"(?P<ts>[^"]+)"\s*\,\s*'
        'nonce\s*=\s*"(?P<nonce>[^"]+)"\s*\,\s*'
        'ext\s*=\s*"(?P<ext>[^"]*)"\s*\,\s*'
        'mac\s*=\s*"(?P<mac>[^"]+)"\s*'
        '$',
        re.IGNORECASE
    )

    def __init__(self, mac_key_identifier, ts, nonce, ext, mac):
        self.mac_key_identifier = mac_key_identifier
        self.ts = ts
        self.nonce = nonce
        self.ext = ext
        self.mac = mac

    def __str__(self):
        return (
            'MAC id="{self.mac_key_identifier}", ts="{self.ts}", '
            'nonce="{self.nonce}", ext="{self.ext}", mac="{self.mac}"'
        ).format(self=self)
