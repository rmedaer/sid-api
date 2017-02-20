"""
Not implemented handler
This handler returns always a "501 - Not implemented" error.
"""

from tornado.web import HTTPError
from .error import ErrorHandler

class NotImplementedHandler(ErrorHandler):
    """ Not implemented handler. See module documentation. """

    def prepare(self):
        """ Almost raise a "501 - Not implemented" error """
        raise HTTPError(
            status_code=501,
            log_message='Not implemented.'
        )
