# -*- coding: utf-8 -*-

""" Version handler

This handler returns the current version of the API.
"""

from .. import __version__
from .error import JsonErrorHandler

class VersionHandler(JsonErrorHandler):
    """ Version handler. See module documentation. """

    def get(self):
        """ Returns the JSON formatted version of the API """
        self.write({
            'version': __version__
        })
