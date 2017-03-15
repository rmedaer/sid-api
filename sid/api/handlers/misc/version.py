"""
This module contains a handler which returns the current version of the API.
"""

from tornado.web import RequestHandler
from sid.api import __version__
from sid.api.http import json_error_handling, available_content_type

@json_error_handling
class VersionHandler(RequestHandler):
    """
    Version handler. See module documentation.
    """

    @available_content_type(['application/json'])
    def get(self, *args, **kwargs):
        """
        Returns the JSON formatted version of the API.
        """
        self.write({
            'version': __version__
        })

    def data_received(self, *args, **kwargs):
        """
        Implementation of astract data_received.
        """
        pass
