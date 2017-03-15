"""
AbstractWarehouseHandler module (see handler documentation)
"""

import os
from tornado.web import HTTPError
from sid.api import http, auth
from sid.api.handlers.workspace import AbstractWorkspaceHandler
from sid.lib.warehouse import Warehouse
from sid.lib.git import OAuthCallback, RepositoryNotFoundException, BranchNotFoundException, ForbiddenException

__repository_name__ = u'warehouse'
__repository_remote_name__ = u'origin'
__repository_remote_path__ = u'gitolite-admin'

@http.json_error_handling
class AbstractWarehouseHandler(AbstractWorkspaceHandler):
    """
    Abstract handler which is preparing a Warehouse for user logged in.
    """

    @auth.require_authentication()
    def prepare(self, **kwargs):
        """
        Instance (and clone if needed) a warehouse (gitolite) repository
        in user workspace.

        It's using `__repository_name__` as local name.
        """
        super(AbstractWarehouseHandler, self).prepare(**kwargs)

        local_path = os.path.join(self.workspace_dir, kwargs['auth']['user'], __repository_name__)
        remote_url = http.join_url_path(self.remote_base_url, __repository_remote_path__)

        # Initialize Warehouse repository
        self.warehouse = Warehouse(local_path)

        # Set Git credentials
        self.warehouse.set_callbacks(
            OAuthCallback(
                kwargs['auth']['user'], # User
                kwargs['auth']['bearer'] # Password (here the token)
            )
        )

        # Try to open Git repository or initialize it
        try:
            self.warehouse.open()
        except RepositoryNotFoundException:
            self.warehouse.initialize()

        # Set user signature
        self.warehouse.set_default_signature(kwargs['auth']['user'], 'TODO') # TODO set mail

        # Make sure 'origin' remote exists
        self.warehouse.set_remote(remote_url, __repository_remote_name__)

        # Update our local copy
        try:
            self.warehouse.pull(__repository_remote_name__)
        except BranchNotFoundException:
            raise HTTPError(
                status_code=500,
                log_message='Remote branch not found in \'gitolite-admin\' repository. '
                            'Please check it manually.'
            )
        except ForbiddenException:
            raise HTTPError(
                status_code=401,
                log_message='You\'re not authorized to manage projects.'
            )

        # Load Pyolite content
        self.warehouse.load()

    def data_received(self, *args, **kwargs):
        """
        Implementation of astract data_received.
        """
        pass
