"""
This module contains a generic handler to abstract user workspace.
"""

import os
import sid.api.http as http
import sid.api.auth as auth
from tornado.web import RequestHandler, HTTPError
from sid.api import __gitolite_admin__, __projects_prefix__, __templates_prefix__
from sid.api.pyolite import PyoliteRepository
from sid.api.cookiecutter import CookiecutterRepository
from sid.api.git import GitRepository, GitRepositoryNotFound, GitRemoteDuplicate, GitBranchNotFound, GitForbidden

@http.json_error_handling
class WorkspaceHandler(RequestHandler):
    """ Abstract handler for Pyolite configuration. """

    def initialize(self):
        """
        Initialize workspace handler.

        Arguments:
        workspace_dir -- Base workspace directory.
        remote_url -- Base remote URL.
        """
        self.workspace_dir = self.application.settings.get('app').get('workspace_dir')
        self.remote_base_url = self.application.settings.get('app').get('remote_url')

    def prepare(self, *args, **kwargs):
        """
        Prepare user's workspace.
        """
        self.prepare_workspace(*args, **kwargs)

    @auth.require_authentication()
    def prepare_workspace(self, *args, **kwargs):
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

    @auth.require_authentication()
    def prepare_pyolite(self, *args, **kwargs):
        """
        Prepare Pyolite repository.
        """
        local_path = os.path.join(self.workspace_dir, kwargs['auth']['user'], 'admin')
        remote_url = http.join_url_path(self.remote_base_url, __gitolite_admin__)

        # Initialize Pyolite repository
        pyolite = PyoliteRepository(local_path)

        # Pull remote
        self.prepare_repository(pyolite, remote_url)

        # Load Pyolite content
        pyolite.load()

        return pyolite

    @auth.require_authentication()
    def prepare_project(self, project_name, *args, **kwargs):
        """
        Prepare a project in user workspace from its name.

        Arguments:
        project_name -- Project name.

        Keyword arguments: (see prepare_repository)
        """
        local_path = os.path.join(self.workspace_dir, kwargs['auth']['user'], __projects_prefix__, project_name)
        remote_url = http.join_url_path(self.remote_base_url, __projects_prefix__, project_name)

        # Initialize Git repository
        project = GitRepository(local_path)

        # Pull remote
        self.prepare_repository(project, remote_url)

        return project

    @auth.require_authentication()
    def prepare_template(self, template_name, *args, **kwargs):
        """
        Prepare a template in user workspace from its name.

        Arguments:
        template_name -- Template name.

        Keyword arguments: (see prepare_repository)
        """
        local_path = os.path.join(self.workspace_dir, kwargs['auth']['user'], __templates_prefix__, template_name)
        remote_url = http.join_url_path(self.remote_base_url, __templates_prefix__, template_name)

        # Initialize Git repository
        template = CookiecutterRepository(local_path)

        # Pull remote
        self.prepare_repository(template, remote_url)

        return template

    @auth.require_authentication()
    def prepare_repository(self, repository, remote_url, *args, **kwargs):
        """
        Try to clone a given repository into user's workspace.

        Arguments:
        repository -- Repository to prepare.
        remote_url -- Repository remote URL.

        Keyword arguments:
        auth -- An dictionnary which contains user settings.
        bearer -- Valid OAuth token used for authentication.
        """
        assert isinstance(repository, GitRepository)

        # Set Git credentials
        repository.set_callbacks(
            auth.OAuthCallback(
                kwargs['auth']['user'], # User
                kwargs['auth']['bearer'] # Password (here the token)
            )
        )

        # Try to open Git repository or initialize it
        try:
            repository.open()
        except GitRepositoryNotFound:
            repository.initialize()

        # Make sure 'origin' remote exists
        try:
            repository.set_remote(remote_url, 'origin')
        except GitRemoteDuplicate:
            pass

        # Update our local copy
        try:
            repository.pull('origin')
        except GitBranchNotFound:
            raise HTTPError(
                status_code=503,
                log_message='Remote or local branch not found. '
                            'Please contact your system administrator.'
            )
        except GitForbidden:
            raise HTTPError(
                status_code=401,
                log_message='You\'re not authorized to access this resource.'
            )

        return repository

    def data_received(self, *args, **kwargs):
        """
        """
        pass
