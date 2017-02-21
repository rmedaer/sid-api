"""
This module contains decorators which manage Content-Type negociation
according to RFC7231 section 3.4 and 5.3.
"""

import mimeparse
from tornado.web import HTTPError

def accepted_content_type(accepted):
    """ Negociate accepted content-type received on POST, PUT and PATCH methods """

    # pylint: disable=C0111
    def _accepted_content_type(func):
        # pylint: disable=C0111
        def wrapper(*args, **kwargs):
            if not accepted:
                raise HTTPError(
                    status_code=500
                )

            header = args[0].request.headers.get('Content-Type')
            if not header:
                raise HTTPError(
                    status_code=400,
                    log_message='Missing \'Content-type\' header.'
                )

            try:
                content_type = mimeparse.best_match(accepted, header)
            except ValueError:
                raise HTTPError(
                    status_code=400,
                    log_message='Malformed \'Content-Type\' header.'
                )

            if not content_type:
                raise HTTPError(
                    status_code=415,
                    log_message='Given Content-Type is not allowed.'
                )

            kwargs['input_content_type'] = content_type
            return func(*args, **kwargs)
        return wrapper
    return _accepted_content_type

def available_content_type(accepted):
    """ Negociate content type wished by HTTP client (header 'Accept') """

    # pylint: disable=C0111
    def _available_content_type(func):
        # pylint: disable=C0111
        def wrapper(*args, **kwargs):
            # If not any content_type given, it returns a internal server error
            if not accepted:
                raise HTTPError(
                    status_code=500
                )

            # Try to find best match between accepted mime types and 'Accept' header
            try:
                content_type = mimeparse.best_match(
                    accepted,
                    args[0].request.headers.get('Accept', '*/*')
                )
            # NOTE should be replaced by MimeTypeParseException (mimeparse >= 1.5.2)
            except ValueError:
                raise HTTPError(
                    status_code=400,
                    log_message='Malformed \'Accept\' header.'
                )

            # If not any match found, return a unsupported media type error
            if not content_type:
                raise HTTPError(
                    status_code=406,
                    log_message='Content type negociation failed. '
                                'Accepted media type are unsupported.'
                )

            # Set up "output" content-type in keyword arguments
            kwargs['output_content_type'] = content_type

            # Set 'Content-Type' header according to Tinder process... 'It's a match !'
            args[0].set_header('Content-Type', content_type)

            return func(*args, **kwargs)
        return wrapper
    return _available_content_type
