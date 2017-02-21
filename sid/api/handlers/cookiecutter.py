"""
This module contains a generic handler which manage Cookiecutter templates.
"""

import os
from tornado.web import HTTPError

from sid.api import __public_key__, __templates_prefix__
from sid.api.auth import require_authentication
from sid.api.auth.oauth_callback import OAuthCallback
from sid.api.cookiecutter import CookiecutterRepository
from sid.api.handlers.error import ErrorHandler
from sid.api.handlers.workspace_handler import WorkspaceHandler
from sid.api.http import join_url_path
from sid.api.git import GitForbidden

class CookiecutterHandler(WorkspaceHandler, ErrorHandler):
    """
    Abstract handler for Cookiecutter template management.
    This handler prepare a Cookiecutter object for inheritance.
    It's inspired from PyoliteHandler.
    """

    def initialize(self, workspaces_dir, remotes_url):
        """
        Initialize cookiecutter handler.
        """
        self.cookiecutter = None
        self.workspaces_dir = workspaces_dir
        self.remotes_url = remotes_url

        WorkspaceHandler.initialize(self, workspaces_dir)

    @require_authentication(__public_key__)
    def prepare(self, name, *args, **kwargs):
        """
        Create and load a cookiecutter repository.
        """
        WorkspaceHandler.prepare(self)

        self.cookiecutter = CookiecutterRepository(
            os.path.join(self.workspaces_dir, kwargs['auth']['mail'], __templates_prefix__, name),
            join_url_path(self.remotes_url, __templates_prefix__, name)
        )

        # Load Cookiecutter repository
        self.cookiecutter.set_callbacks(OAuthCallback(kwargs['auth']['mail'], kwargs['bearer']))
        try:
            self.cookiecutter.load()
        except GitForbidden:
            raise HTTPError(
                status_code=403,
                log_message='You are not authorize to use this template'
            )
