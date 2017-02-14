# -*- coding: utf-8 -*-

""" Error handler

This handler translate raised HTTPError into understandable and formatted
error message.
"""

from tornado.web import RequestHandler

class ErrorHandler(RequestHandler):
    """ Error handler.

    Format raised HTTPError into JSON format.
    """

    def write_error(self, status_code, **kwargs):
        # Fetch error message
        _, err, _ = kwargs['exc_info']
        log_message = err.log_message if hasattr(err, 'log_message') else None

        if status_code == 405 and not log_message: # pragma: no cover
            # NOTE could be tested by defining a new custom handlers in tests ...
            # I don't think it's really usefull.
            log_message = 'This method is not allowed.'

        # Send error object
        self.set_header('Content-Type', 'application/json')
        self.write({
            'code': status_code,
            'message': log_message
        })

    def data_received(self, chunk): # pragma: no cover
        """ Not implemented ! """
        return
