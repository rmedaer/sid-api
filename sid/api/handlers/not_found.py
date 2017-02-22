"""
This module contians the fallback handler. It will almost raise with a
'404 - Not Found' error.
"""

from tornado.web import RequestHandler, HTTPError
from sid.api.http import json_error_handling

@json_error_handling
class NotFoundHandler(RequestHandler):
    """
    Default handler. See module documentation.
    """

    def prepare(self):
        """
        Almost raise a '404 - Not Found' error
        """
        raise HTTPError(
            status_code=404,
            log_message='Resource not found.'
        )
