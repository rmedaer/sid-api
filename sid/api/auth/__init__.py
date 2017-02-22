"""
This module contains decorator needed for SID API authentication.
"""

import json
import jwt
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidIssuedAtError,
    ImmatureSignatureError,
    InvalidKeyError,
    InvalidAlgorithmError,
    InvalidTokenError
)
from tornado.web import HTTPError, RequestHandler
from oauth_callback import OAuthCallback

def require_authentication(public_key):
    # pylint: disable=C0111
    def _require_authentication(func):
        # pylint: disable=C0111
        def wrapper(*args, **kwargs):
            handler = args[0]
            if not isinstance(handler, RequestHandler):
                raise HTTPError(
                    status_code=500,
                    log_message='Authentication decorator error. '
                                'Please contact your administrator.'
                )

            auth_header = handler.request.headers.get('Authorization')
            if auth_header is None:
                # TODO We should answer with WWW-Authenticate header "bearer"
                raise HTTPError(
                    status_code=401,
                    log_message='Please provide an \'Authorization\' header'
                )

            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                # TODO We should answer with WWW-Authenticate header "bearer"
                raise HTTPError(
                    status_code=401,
                    log_message='Malformed \'Authorization\' header'
                )

            try:
                decoded = jwt.decode(
                    parts[1],
                    public_key
                )
            except (DecodeError,
                    ExpiredSignatureError,
                    InvalidAudienceError,
                    InvalidIssuerError,
                    InvalidIssuedAtError,
                    ImmatureSignatureError,
                    InvalidKeyError,
                    InvalidAlgorithmError,
                    InvalidTokenError):
                # TODO We should answer with WWW-Authenticate header "bearer"
                raise HTTPError(
                    status_code=401,
                    log_message='Token validation failed'
                )

            kwargs['bearer'] = parts[1]
            kwargs['auth'] = decoded

            return func(*args, **kwargs)
        return wrapper
    return _require_authentication
