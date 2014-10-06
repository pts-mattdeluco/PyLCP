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
    """Implements the notion of the ext as described in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.1"""

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
    """Implements the notion of a normalized request string as described in
    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-02#section-3.2.1"""

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
    """Generates a random string intend for use as a nonce when computing an
    HMAC."""
    return base64.b64encode(os.urandom(8))


def generate_signature(mac_key, normalized_request_string):
    """Generate a request's MAC given a normalized request string (aka
    a summary of the key elements of the request and the mac key (shared
    secret)."""
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
    the value for the HTTP Authorization header using an existing hmac."""

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
