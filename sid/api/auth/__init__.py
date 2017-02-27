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
from jwt.contrib.algorithms.pycrypto import RSAAlgorithm

__jwt_algorithms__ = {
    'RS256': RSAAlgorithm(RSAAlgorithm.SHA256),
    'RS384': RSAAlgorithm(RSAAlgorithm.SHA384),
    'RS512': RSAAlgorithm(RSAAlgorithm.SHA512)
}

# I don't know why but on production baseline RS256 was not registered
# automatically, so we are trying to register them
# Since we only accept RSA PKI as JWT tokens (see rfc7518 section 3.1)
# we are using the following list:
for algorithm in __jwt_algorithms__:
    try:
        jwt.register_algorithm(algorithm, __jwt_algorithms__[algorithm])
    except ValueError as err:
        if err.message == 'Algorithm already has a handler.':
            # Well, if the algorithm is almost registered, pass.
            continue
        raise err

def require_authentication():
    # pylint: disable=C0111
    def _require_authentication(func): # pylint: disable=C0111
        # Func argument MUST be callable
        assert callable(func)

        def wrapper(*args, **kwargs):
            """
            Replace original function by this one. As any wrapper it's calling
            original function after authentication validation.
            """
            handler = args[0]

            # Decorated function must be a method of RequestHandler
            assert isinstance(handler, RequestHandler)

            # Get authentication settings from application handler
            settings = handler.application.settings.get('auth', {})

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
                    settings.get('public_key'),
                    audience=settings.get('audience', 'sid'),
                    algorithms=[settings.get('algorithm', 'RS256')]
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

            # Get userfield from decoded payload
            user_field = settings.get('username_field', 'user')
            user = decoded.get(user_field)
            if not user:
                raise HTTPError(
                    status_code=403,
                    log_message='Missing JWT tuple: %s' % user_field
                )

            kwargs['auth'] = {
                'bearer': parts[1],
                'payload': decoded,
                'user': user
            }

            return func(*args, **kwargs)
        return wrapper
    return _require_authentication
