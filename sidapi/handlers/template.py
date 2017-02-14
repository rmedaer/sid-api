# -*- coding: utf-8 -*-

""" Template handler

This module contains the handler which manage templates.
"""

# Global imports
from tornado.web import HTTPError
from pyolite2 import RepositoryNotFoundError

# Local imports
from sidapi import __templates_prefix__
from .error import ErrorHandler
from .serializer import SerializerHandler
from .template_collection import TemplateCollectionHandler
from sidapi.decorators.content_negociation import negociate_content_type

class TemplateHandler(TemplateCollectionHandler, ErrorHandler, SerializerHandler):
    """ RequestHandler to CRUD template. """

    @negociate_content_type(['application/json'])
    def get(self, name):
        """ Fetch template from its name. """
        try:
            self.write(self.pyolite.repos[__templates_prefix__ + name])

            # TODO get template properties (documentation)

            # TODO get template schema if available

        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Template not found.'
            )
