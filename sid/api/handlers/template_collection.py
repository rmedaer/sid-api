# -*- coding: utf-8 -*-

""" This module contains handler which manage a template collection
from Gitolite configuration. """

# Local imports
from sid.api import __templates_prefix__, __public_key__
from sid.api.auth import require_authentication
from sid.api.handlers.error import ErrorHandler
from sid.api.handlers.serializer import SerializerHandler
from sid.api.handlers.pyolite import PyoliteHandler
from sid.api.http import available_content_type

class TemplateCollectionHandler(PyoliteHandler, ErrorHandler, SerializerHandler):
    """ This handler manage templates from Pyolite configuration. """

    @require_authentication(__public_key__)
    @available_content_type(['application/json'])
    def get(self, *args, **kwargs):
        """ List available templates. """

        self.write([project
                    for project in self.pyolite.repos
                    if project.name.startswith(__templates_prefix__)])
