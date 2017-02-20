# -*- coding: utf-8 -*-

""" This module contains a generic handler to abstract user workspace. """

import os

from tornado.web import HTTPError
from sid.api import __public_key__
from sid.api.handlers.error import ErrorHandler
from sid.api.auth import require_authentication

def is_safe_path(basedir, path, follow_symlinks=True):
    """ Ensure given path is safe or not """
    if follow_symlinks:
        return os.path.realpath(path).startswith(basedir)
    return os.path.abspath(path).startswith(basedir)

class WorkspaceHandler(ErrorHandler):
    """ Abstract handler for Pyolite configuration. """

    def initialize(self, workspace_dir):
        """ Initialize workspace handler. """

        self.workspace_dir = workspace_dir

    @require_authentication(__public_key__)
    def prepare(self, **kwargs):
        """ Change current working directory. """

        user_workspace_dir = os.path.join(self.workspace_dir, kwargs['auth']['mail'])
        if not is_safe_path(self.workspace_dir, user_workspace_dir):
            # Attempt to hack using path traversal
            raise HTTPError(
                status_code=418,
                reason='I\'m a teapot',
                log_message='Nice try ! '
                            'Feel free to contribute to our project if you find bugs.'
            )

        # Test if directory exists or create it
        if not os.path.exists(user_workspace_dir):
            os.makedirs(user_workspace_dir)

        # Change directory
        os.chdir(user_workspace_dir)

        super(WorkspaceHandler, self).prepare()
