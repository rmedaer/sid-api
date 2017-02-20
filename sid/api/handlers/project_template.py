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
from sid.api.cookiecutter import CookiecutterRepository
from sid.api.handlers.cookiecutter import CookiecutterHandler
from sid.api.handlers.error import ErrorHandler
from sid.api.handlers.serializer import SerializerHandler
from sid.api.handlers.pyolite import PyoliteHandler
from sid.api.http import (
    available_content_type,
    accepted_content_type,
    parse_json_body,
    join_url_path
)

class ProjectTemplateHandler(
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

    @require_authentication(__public_key__)
    def prepare(self, *args, **kwargs):
        """
        Prepare each parent handler.
        """
        PyoliteHandler.prepare(self, *args, **kwargs)

    @accepted_content_type(['application/json'])
    @available_content_type(['application/json'])
    @parse_json_body()
    def post(self, project_name, *args, **kwargs):
        CookiecutterHandler.prepare(self, kwargs['json']['name'], *args, **kwargs)
