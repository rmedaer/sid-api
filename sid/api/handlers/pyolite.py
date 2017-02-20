# -*- coding: utf-8 -*-

""" This module contains a generic handler which manage initialize and prepare
a Pyolite configuration. """

import os
import posixpath
from urlparse import urlsplit, urlunsplit
from sid.api import __public_key__
from sid.api.auth import require_authentication
from sid.api.auth.oauth_callback import OAuthCallback
from sid.api.handlers.error import ErrorHandler
from sid.api.handlers.workspace_handler import WorkspaceHandler
from sid.api.pyolite import PyoliteRepository

ADMIN_REPOSITORY = 'gitolite-admin'

def join_url_path(url, additional_path):
    """
    Join URL path with given one.
    """
    scheme, loc, path, query, fragments = urlsplit(url)
    path = posixpath.join(path, additional_path)
    return urlunsplit((scheme, loc, path, query, fragments))

class PyoliteHandler(WorkspaceHandler, ErrorHandler):
    """ Abstract handler for Pyolite configuration. """

    def initialize(self, workspaces_dir, remotes_url):
        """ Initialize pyolite handler. Storing admin_config path. """

        self.pyolite = None
        self.workspaces_dir = workspaces_dir
        self.remotes_url = remotes_url

        WorkspaceHandler.initialize(self, workspaces_dir)

    @require_authentication(__public_key__)
    def prepare(self, **kwargs):
        """ Prepare handler by instanciating and loading Pyolite configuration. """

        WorkspaceHandler.prepare(self)

        # Initialize Pyolite configuration object
        self.pyolite = PyoliteRepository(
            os.path.join(self.workspaces_dir, kwargs['auth']['mail'], ADMIN_REPOSITORY),
            join_url_path(self.remotes_url, ADMIN_REPOSITORY)
        )

        # Set Pyolite credentials
        self.pyolite.set_callbacks(OAuthCallback(kwargs['auth']['mail'], kwargs['bearer']))

        # Load Pyolite repository
        self.pyolite.load()
