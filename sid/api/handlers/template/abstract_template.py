"""
AbstractTemplateHandler module (see handler documentation)
"""

import os
from tornado.web import HTTPError
from sid.api import http, auth
from sid.api.handlers.workspace import AbstractWorkspaceHandler
from sid.lib.template import Template
from sid.lib.git import (
    OAuthCallback,
    RepositoryNotFoundException,
    BranchNotFoundException,
    ForbiddenException
)

__templates_prefix__ = 'templates/'

@http.json_error_handling
class AbstractTemplateHandler(AbstractWorkspaceHandler):
    """
    Abstract handler which is preparing a project repository for user logged in.
    """

    @auth.require_authentication()
    def prepare_template(self, template_name, **kwargs):
        """
        Prepare a template in user workspace from its name.

        Arguments:
        template_name -- Template name.

        Keyword arguments: (see prepare_repository)
        """
        local_path = os.path.join(self.workspace_dir, kwargs['auth']['user'], __templates_prefix__, template_name)
        remote_url = http.join_url_path(self.remote_base_url, __templates_prefix__, template_name)

        # Initialize Git repository
        self.template = Template(local_path)

        # Set Git credentials
        self.template.set_callbacks(
            OAuthCallback(
                kwargs['auth']['user'], # User
                kwargs['auth']['bearer'] # Password (here the token)
            )
        )

        # Try to open Git repository or initialize it
        try:
            self.template.open()
        except RepositoryNotFoundException:
            self.template.initialize()

        # Set user signature
        self.template.set_default_signature(kwargs['auth']['user'], 'TODO') # TODO set mail

        # Make sure 'origin' remote exists
        self.template.set_remote(remote_url, 'origin')

        # Update our local copy
        try:
            self.template.pull('origin')
        except BranchNotFoundException:
            raise HTTPError(
                status_code=503,
                log_message='Remote or local branch not found. '
                            'Please contact your system administrator.'
            )
        except ForbiddenException:
            raise HTTPError(
                status_code=401,
                log_message='You\'re not authorized to access this template.'
            )

        return self.template

    def data_received(self, *args, **kwargs):
        """
        Implementation of astract data_received.
        """
        pass
