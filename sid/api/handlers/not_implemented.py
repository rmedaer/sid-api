"""
Not implemented handler.
This handler returns always a "501 - Not implemented" error.
"""

from tornado.web import RequestHandler, HTTPError
from sid.api.http import json_error_handling

@json_error_handling
class NotImplementedHandler(RequestHandler):
    """
    Not implemented handler. See module documentation.
    """

    def prepare(self):
        """
        Almost raise a '501 - Not implemented' error
        """
        raise HTTPError(
            status_code=501,
            log_message='Not implemented.'
        )

    def data_received(self, *args, **kwargs):
        """
        Implementation of astract data_received.
        """
        pass
