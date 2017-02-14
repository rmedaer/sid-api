# -*- coding: utf-8 -*-

""" This module contains handler which manage a template collection
from Gitolite configuration. """

# Global imports
from tornado.web import HTTPError

# Local imports
from sidapi import __templates_prefix__
from .error import ErrorHandler
from .serializer import SerializerHandler
from sidapi.helpers import PyoliteRepository
from sidapi.decorators.content_negociation import negociate_content_type

class TemplateCollectionHandler(ErrorHandler, SerializerHandler):
    """ This handler manage templates from Pyolite configuration. """

    def initialize(self, admin_config):
        """ Initialize the handler with admin_config. """

        self.pyolite = None
        self.admin_config = admin_config

    def prepare(self):
        """ Prepare request handling: try to instanciate and load Pyolite config. """

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

        self.write([project
                    for project in self.pyolite.repos
                    if project.name.startswith(__templates_prefix__)])
