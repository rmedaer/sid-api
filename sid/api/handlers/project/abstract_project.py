"""
AbstractProjectHandler module (see handler documentation)
"""

import os
from tornado.web import HTTPError
from sid.api import http, auth
from sid.api.handlers.workspace import AbstractWorkspaceHandler
from sid.lib.project import Project
from sid.lib.git import (
    OAuthCallback,
    RepositoryNotFoundException,
    BranchNotFoundException,
    ForbiddenException
)

__projects_prefix__ = 'projects/'

@http.json_error_handling
class AbstractProjectHandler(AbstractWorkspaceHandler):
    """
    Abstract handler which is preparing a project repository for user logged in.
    """

    @auth.require_authentication()
    def prepare_project(self, project_name, **kwargs):
        """
        Prepare a project in user workspace from its name.

        Arguments:
        project_name -- Project name.
        """
        local_path = os.path.join(self.workspace_dir, kwargs['auth']['user'], __projects_prefix__, project_name)
        remote_url = http.join_url_path(self.remote_base_url, __projects_prefix__, project_name)

        # Initialize Git repository
        self.project = Project(local_path)

        # Set Git credentials
        self.project.set_callbacks(
            OAuthCallback(
                kwargs['auth']['user'], # User
                kwargs['auth']['bearer'] # Password (here the token)
            )
        )

        # Try to open Git repository or initialize it
        try:
            self.project.open()
        except RepositoryNotFoundException:
            self.project.initialize()

        # Set user signature
        self.project.set_default_signature(kwargs['auth']['user'], 'TODO') # TODO set mail

        # Make sure 'origin' remote exists
        self.project.set_remote(remote_url, 'origin')

        # Update our local copy
        try:
            self.project.pull('origin')
        except BranchNotFoundException:
            raise HTTPError(
                status_code=503,
                log_message='Remote or local branch not found. '
                            'Please contact your system administrator.'
            )
        except ForbiddenException:
            raise HTTPError(
                status_code=401,
                log_message='You\'re not authorized to access this resource.'
            )

        return self.project

    def data_received(self, *args, **kwargs):
        """
        Implementation of astract data_received.
        """
        pass
