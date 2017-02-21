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
from sid.api.git import GitForbidden
from sid.api.handlers.cookiecutter import CookiecutterHandler
from sid.api.handlers.error import ErrorHandler
from sid.api.handlers.serializer import SerializerHandler
from sid.api.handlers.workspace_handler import WorkspaceHandler
from sid.api.http import (
    available_content_type,
    accepted_content_type,
    parse_json_body,
    join_url_path
)

class ProjectTemplateHandler(
        WorkspaceHandler,
        ErrorHandler,
        SerializerHandler
    ):
    """
    """

    @require_authentication(__public_key__)
    @accepted_content_type(['application/json'])
    @available_content_type(['application/json'])
    @parse_json_body()
    def post(self, project_name, *args, **kwargs):
        template_name = json['name']

        # Initialize template repository
        template = CookiecutterRepository(
            os.path.join(self.workspaces_dir, kwargs['auth']['mail'], __templates_prefix__, template_name),
            join_url_path(self.remotes_url, __templates_prefix__, template_name)
        )

        # Load Cookiecutter repository
        template.set_callbacks(OAuthCallback(kwargs['auth']['mail'], kwargs['bearer']))
        try:
            template.load()
        except GitForbidden:
            raise HTTPError(
                status_code=403,
                log_message='You are not authorize to use this template'
            )

        # Apply it to our repository
        # template.apply(os.path.join(self.workspaces_dir, kwargs['auth']['mail'], __templates_prefix__, project_name))
