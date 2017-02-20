"""
This module contains the handler which retrieve template information.
"""

# Global imports
import os
from tornado.web import HTTPError, RequestHandler
from pyolite2 import RepositoryNotFoundError

# Local imports
from sid.api import __templates_prefix__, __public_key__
from sid.api.auth import require_authentication
from sid.api.auth.oauth_callback import OAuthCallback
from sid.api.handlers.cookiecutter import CookiecutterHandler
from sid.api.handlers.error import ErrorHandler
from sid.api.handlers.serializer import SerializerHandler
from sid.api.handlers.pyolite import PyoliteHandler
from sid.api.http import available_content_type, join_url_path
from sid.api.cookiecutter import CookiecutterRepository

class TemplateHandler(
        CookiecutterHandler,
        PyoliteHandler,
        ErrorHandler,
        SerializerHandler
    ):
    """
    RequestHandler to CRUD template.
    """

    def initialize(self, workspaces_dir, remotes_url):
        """
        Initialize each parent handler.
        """
        CookiecutterHandler.initialize(self, workspaces_dir, remotes_url)
        PyoliteHandler.initialize(self, workspaces_dir, remotes_url)

    def prepare(self, *args, **kwargs):
        """
        Prepare each parent handler.
        """
        CookiecutterHandler.prepare(self, self.path_args[0], *args, **kwargs)
        PyoliteHandler.prepare(self, *args, **kwargs)

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

        # Set 'Content-Type' header according to Tinder process... 'It's a match !'
        self.set_header('Content-Type', output_content_type)

        if output_content_type == 'application/json':
            self.write(repo)

        elif output_content_type == 'application/schema+json':
            self.write(self.cookiecutter.get_schema())

        elif output_content_type == 'text/markdown':
            RequestHandler.write(self, self.cookiecutter.get_readme())
