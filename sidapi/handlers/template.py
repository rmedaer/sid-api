# -*- coding: utf-8 -*-

# Global imports
from tornado.web import HTTPError
from pyolite2 import RepositoryNotFoundError

# Local imports
from .. import __templates_prefix__
from .error import ErrorHandler
from .serializer import SerializerHandler
from .template_collection import TemplateCollectionHandler
from ..helpers import PyoliteRepository
from ..decorators import negociate_content_type

class TemplateHandler(TemplateCollectionHandler, ErrorHandler, SerializerHandler):

    @negociate_content_type(['application/json'])
    def get(self, name):
        """ Fetch template from its name. """
        try:
            self.write(self.pyolite.repos[__templates_prefix__ + name])
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Template not found.'
            )
