# -*- coding: utf-8 -*-

""" Version handler

This handler returns the current version of the API.
"""

from sidapi import __version__
from .error import ErrorHandler
from sidapi.decorators.content_negociation import available_content_type

class VersionHandler(ErrorHandler):
    """ Version handler. See module documentation. """

    @available_content_type(['application/json'])
    def get(self, *args, **kwargs):
        """ Returns the JSON formatted version of the API """
        self.write({
            'version': __version__
        })
