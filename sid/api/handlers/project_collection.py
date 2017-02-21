"""
This module contains handler which manage a project collection
from Gitolite configuration.
"""

# Global imports
from jsonpatch import make_patch
from tornado.web import HTTPError
from pyolite2 import RepositoryDuplicateError, Repository

# Local imports
import sid.api.auth as auth
import sid.api.http as http
from sid.api import __projects_prefix__, __public_key__
from sid.api.git import GitForbidden
from sid.api.handlers.workspace import WorkspaceHandler
from sid.api.pyolite import patch_pyolite_repo
from sid.api.schemas import PROJECT_SCHEMA

@http.json_error_handling
@http.json_serializer
class ProjectCollectionHandler(WorkspaceHandler):
    """
    This handler process following routes:

        - GET  /projects -- List projects
        - POST /projects -- Create a new project
    """

    def prepare(self, *args, **kwargs):
        """
        Prepare user's workspace and Pyolite configuration to manage projects.
        """
        super(ProjectCollectionHandler, self).prepare()
        self.pyolite = self.prepare_pyolite()

    @http.available_content_type(['application/json'])
    def get(self, *args, **kwargs):
        """
        List all projects.

        Example:
        > GET /projects HTTP/1.1
        > Accept: */*
        >
        """
        self.write([project
                    for project in self.pyolite.repos
                    if project.name.startswith(__projects_prefix__)])

    @auth.require_authentication(__public_key__)
    @http.accepted_content_type(['application/json'])
    @http.available_content_type(['application/json'])
    @http.parse_json_body(PROJECT_SCHEMA)
    def post(self, *args, **kwargs):
        """
        Create and add a new project.

        Example:
        > POST /projects HTTP/1.1
        > Accept: */*
        > Content-Type: application/json
        > Content-Length: 64
        >
        {"name":"test-project","rules":[{"users":["@all"],"perm":"RW"}]}
        """

        try:
            # Create and add repository
            repo = Repository(__projects_prefix__ + kwargs['json']['name'])
            self.pyolite.repos.append(repo)

            # Add user permissions by patching repo
            patch_pyolite_repo(
                repo,
                make_patch(
                    http.Encoder().default(repo),
                    kwargs['json']
                )
            )
        except RepositoryDuplicateError:
            raise HTTPError(
                status_code=409,
                log_message='Repository \'%s\' already exists' % kwargs['json']['name']
            )

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Created project \'%s\'' % kwargs['json']['name'])
        except GitForbidden:
            raise HTTPError(
                status_code=403,
                log_message='You are not authorized to create projects'
            )
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return created repository
        self.write(repo)
