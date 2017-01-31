# -*- coding: utf-8 -*-

""" JSON error handler

This handler translate raised HTTPError into understandable and formatted
error message.
"""

from tornado.web import RequestHandler

class JsonErrorHandler(RequestHandler):
    """ JSON error handler.

    Format raised HTTPError into JSON format.
    """

    def write_error(self, status_code, **kwargs):
        """ Format error into JSON format.

        Override write_error method from RequestHandler.
        """
        # Fetch error message
        _, err, _ = kwargs['exc_info']
        log_message = err.log_message if err.log_message else None

        # Send error object
        self.set_header('Content-Type', 'application/json')
        self.write({
            'code': status_code,
            'message': log_message
        })

    def data_received(self, chunk):
        """ Not implemented ! """
        return
