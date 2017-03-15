"""
AbstractWorkspaceHandler module (see handler documentation)
"""

import os
from tornado.web import RequestHandler, HTTPError
from sid.api import http, auth

@http.json_error_handling
class AbstractWorkspaceHandler(RequestHandler):
    """
    Abstract handler which is preparing user's workspace.

    It create a dedicated directory in 'workspace_dir' with logged in user name.
    """

    def initialize(self):
        """
        Initialize workspace handler.

        Arguments:
        workspace_dir -- Base workspace directory.
        remote_url -- Base remote URL.
        """
        self.workspace_dir = self.application.settings.get('app').get('workspace_dir')
        self.remote_base_url = self.application.settings.get('app').get('remote_url')

    @auth.require_authentication()
    def prepare(self, **kwargs):
        """
        Change working directory to user's workspace.
        Since we need to play with per user directory, authentication is
        required.

        Keyword arguments:
        auth -- An dictionnary which contains user settings.
        """
        user_workspace_dir = os.path.join(self.workspace_dir, kwargs['auth']['user'])

        # Be sure the path is safe even it's calculated from signed JWT.
        # If an attempt to hack using path traversal is detected, offer a job !
        if not http.is_safe_path(self.workspace_dir, user_workspace_dir):
            raise HTTPError(
                status_code=418,
                reason='I\'m a teapot',
                log_message='Nice try ! '
                            'Feel free to contribute to our project if you find bugs.'
            )

        # Test if directory exists or create it
        if not os.path.exists(user_workspace_dir):
            os.makedirs(user_workspace_dir)

        # Change working directory
        os.chdir(user_workspace_dir)

    def data_received(self, *args, **kwargs):
        """
        Implementation of astract data_received.
        """
        pass
