# -*- coding: utf-8 -*-

# Global imports
from tornado.web import HTTPError

# Local imports
from .. import __templates_prefix__
from .error import ErrorHandler
from .serializer import SerializerHandler
from ..helpers import PyoliteRepository
from ..decorators import negociate_content_type

class TemplateCollectionHandler(ErrorHandler, SerializerHandler):
    """ This handler manage templates from Pyolite configuration. """

    def initialize(self, admin_config):
        self.pyolite = None
        self.admin_config = admin_config

    def prepare(self):
        self.pyolite = PyoliteRepository(self.admin_config)

        try:
            self.pyolite.load()
        except:
            raise HTTPError(
                status_code=503,
                log_message='Templates management temporary unavailable.'
            )

    @negociate_content_type(['application/json'])
    def get(self):
        """ List available templates. """
        def projects_filter(project):
            return project.name.startswith(__templates_prefix__)

        self.write(filter(projects_filter, self.pyolite.repos))
