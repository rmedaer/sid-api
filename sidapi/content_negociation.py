# -*- coding: utf-8 -*-

""" Content type negociation module.

This module contains helper to negociate HTTP content type.
"""

import mimeparse
from tornado.web import RequestHandler, HTTPError

class Negociator(RequestHandler):
    """ Abstract request handler to negociate content type.

    This handler expose methods to negociate incoming content type (within 'Accept'
    header). It's finding the best match with accepted mime types.
    """

    def negociate_content_type(self, accepted, apply_content_type=True):
        """ Negociate content-type from incoming request ('accept' header) """

        # If not any content_type given, it returns a internal server error
        if not accepted:
            raise HTTPError(
                status_code=500
            )

        # Try to find best match between accepted mime types and 'Accept' header
        try:
            content_type = mimeparse.best_match(accepted, self.request.headers.get('Accept', '*/*'))
        except ValueError: # NOTE should be replaced by MimeTypeParseException (mimeparse >= 1.5.2)
            raise HTTPError(
                status_code=400,
                log_message='Malformed \'Accept\' header.'
            )

        # If not any match found, return a unsupported media type error
        if not content_type:
            raise HTTPError(
                status_code=415,
                log_message='Content type negociation failed. Accepted media type are unsupported.'
            )

        # Apply output content type if asked
        if apply_content_type:
            self.set_header('Content-Type', content_type)

        return content_type

    def data_received(self, chunk):
        """ Not implemented ! """
        return
