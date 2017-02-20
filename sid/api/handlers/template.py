# -*- coding: utf-8 -*-

""" Template handler

This module contains the handler which manage templates.
"""

# Global imports
import os
from tornado.web import HTTPError, RequestHandler
from pyolite2 import RepositoryNotFoundError

# Local imports
from sid.api import __templates_prefix__, __public_key__
from sid.api.auth import require_authentication
from sid.api.auth.oauth_callback import OAuthCallback
from sid.api.handlers.error import ErrorHandler
from sid.api.handlers.serializer import SerializerHandler
from sid.api.handlers.pyolite import PyoliteHandler
from sid.api.http import available_content_type, join_url_path
from sid.api.cookiecutter import CookiecutterRepository

class TemplateHandler(PyoliteHandler, ErrorHandler, SerializerHandler):
    """ RequestHandler to CRUD template. """

    @require_authentication(__public_key__)
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

        # If user only need high level project configuration
        # we can only return it, ...
        if output_content_type == 'application/json':
            self.write(repo)
            return

        # ... otherwise we have to clone it
        cookiecutter = CookiecutterRepository(
            os.path.join(self.workspaces_dir, kwargs['auth']['mail'], __templates_prefix__, name),
            join_url_path(self.remotes_url, __templates_prefix__, name)
        )

        # Set Pyolite credentials
        cookiecutter.set_callbacks(OAuthCallback(kwargs['auth']['mail'], kwargs['bearer']))

        cookiecutter.load()

        # Set 'Content-Type' header according to Tinder process... 'It's a match !'
        self.set_header('Content-Type', output_content_type)

        if output_content_type == 'application/schema+json':
            self.write(cookiecutter.get_schema())

        elif output_content_type == 'text/markdown':
            RequestHandler.write(self, cookiecutter.get_readme())
