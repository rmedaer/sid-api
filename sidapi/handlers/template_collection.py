# -*- coding: utf-8 -*-

""" This module contains handler which manage a template collection
from Gitolite configuration. """

# Local imports
from sidapi import __templates_prefix__
from sidapi.handlers.error import ErrorHandler
from sidapi.handlers.serializer import SerializerHandler
from sidapi.handlers.pyolite import PyoliteHandler
from sidapi.decorators.content_negociation import negociate_content_type

class TemplateCollectionHandler(PyoliteHandler, ErrorHandler, SerializerHandler):
    """ This handler manage templates from Pyolite configuration. """

    @negociate_content_type(['application/json'])
    def get(self):
        """ List available templates. """

        self.write([project
                    for project in self.pyolite.repos
                    if project.name.startswith(__templates_prefix__)])
