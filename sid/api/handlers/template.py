# -*- coding: utf-8 -*-

""" Template handler

This module contains the handler which manage templates.
"""

# Global imports
from tornado.web import HTTPError
from pyolite2 import RepositoryNotFoundError

# Local imports
from sid.api import __templates_prefix__
from sid.api.handlers.error import ErrorHandler
from sid.api.handlers.serializer import SerializerHandler
from sid.api.handlers.pyolite import PyoliteHandler
from sid.api.decorators.content_negociation import available_content_type

class TemplateHandler(PyoliteHandler, ErrorHandler, SerializerHandler):
    """ RequestHandler to CRUD template. """

    @available_content_type([
        'text/markdown',
        'application/schema+json',
        'application/json'
    ])
    def get(self, name, *args, **kwargs):
        """ Fetch template from its name. """

        output_content_type = kwargs.get('output_content_type')

        # Get repository
        try:
            repo = self.pyolite.repos[__templates_prefix__ + name]
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Template not found.'
            )

        if output_content_type == 'application/json':
            self.write(repo)
        elif output_content_type == 'application/schema+json':
            # TODO get template schema if available
            raise HTTPError(
                status_code=501,
                log_message='Currently not implemented.'
            )

        elif output_content_type == 'text/markdown':
            # TODO get template documentation (README file)
            raise HTTPError(
                status_code=501,
                log_message='Currently not implemented.'
            )
