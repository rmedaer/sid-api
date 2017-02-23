"""
Project handlers.
This module contains every handlers for project management.
"""

# Global imports
from jsonpatch import make_patch
from tornado.web import HTTPError
from pyolite2 import (
    Repository,
    RepositoryNotFoundError,
    RepositoryDuplicateError
)

# Local imports
import sid.api.http as http
import sid.api.auth as auth
from sid.api import __projects_prefix__, __public_key__
from sid.api.git import GitForbidden
from sid.api.schemas import PROJECT_SCHEMA, PROJECT_PATCH_SCHEMA
from sid.api.handlers.workspace import WorkspaceHandler
from sid.api.pyolite import patch_pyolite_repo

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

@http.json_error_handling
@http.json_serializer
class ProjectHandler(WorkspaceHandler):
    """
    This handler process following routes:

        - GET    /projects/<project_name> -- Get project information
        - PUT    /projects/<project_name> -- Update a given project
        - DELETE /projects/<project_name> -- Remove a given project
        - PATCH  /projects/<project_name> -- Patch a given project
    """

    def prepare(self, *args, **kwargs):
        """
        Prepare user's workspace and Pyolite configuration to manage projects.
        """
        super(ProjectHandler, self).prepare()
        self.pyolite = self.prepare_pyolite()

    @auth.require_authentication(__public_key__)
    @http.available_content_type(['application/json'])
    def get(self, name, *args, **kwargs):
        """
        Get project information from its name.

        Example:
        > GET /projects/example HTTP/1.1
        > Accept: */*
        >
        """
        try:
            self.write(self.pyolite.repos[__projects_prefix__ + name])
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

    @auth.require_authentication(__public_key__)
    @http.available_content_type(['application/json'])
    @http.accepted_content_type(['application/json'])
    @http.parse_json_body(PROJECT_SCHEMA)
    def put(self, name, *args, **kwargs):
        """
        Modify a given project.

        Example:
        > PUT /projects/example HTTP/1.1
        > Accept: */*
        > Content-Type: application/json
        > Content-Length: 59
        >
        {"name":"example","rules":[{"users":["@all"],"perm":"RW"}]}
        """
        try:
            repo = self.pyolite.repos[__projects_prefix__ + name]
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

        # Generate patch/diff between existing repo and request body
        patches = make_patch(http.Encoder().default(repo), kwargs['json'])

        # Skip if nothing changed
        if not patches:
            self.write(repo)
            return

        # Patch the diff
        patch_pyolite_repo(
            repo,
            patches
        )

        # Save Gitolite configuration and commit changes
        try:
            self.pyolite.save('Updated project \'%s\'' % name)
        except GitForbidden:
            raise HTTPError(
                status_code=403,
                log_message='You are not authorized to update this project\'s configuration'
            )
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return updated repository
        self.write(repo)

    @auth.require_authentication(__public_key__)
    @http.available_content_type(['application/json'])
    @http.accepted_content_type(['application/json'])
    @http.parse_json_body(PROJECT_PATCH_SCHEMA)
    def patch(self, name, *args, **kwargs):
        """
        Modify a given project from a JSON diff/patch.

        Example:
        > PATCH /projects/example HTTP/1.1
        > Accept: */*
        > Content-Type: application/json
        > Content-Length: 65
        >
        [{"op":"replace","path":"/rules/0","value":{"perm":"RW","users":["@all"]}}]
        """
        patches = kwargs['json']

        try:
            repo = self.pyolite.repos[__projects_prefix__ + name]
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

        # Skip if patch is empty
        if not patches:
            self.write(repo)
            return

        patch_pyolite_repo(repo, patches)

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Updated project \'%s\'' % name)
        except GitForbidden:
            raise HTTPError(
                status_code=403,
                log_message='You are not authorized to patch project\'s configuration'
            )
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return updated repository
        self.write(repo)

    @auth.require_authentication(__public_key__)
    def delete(self, name, *args, **kwargs):
        """
        Delete a project.

        Example:
        > delete /projects/example HTTP/1.1
        > Accept: */*
        >

        NOTE: My editor syntax is bugging when I write "delete" in caps... :-(
        """
        try:
            self.pyolite.repos.remove(__projects_prefix__ + name)
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Removed project \'%s\'' % name)
        except GitForbidden:
            raise HTTPError(
                status_code=403,
                log_message='You are not authorized to remove this project'
            )
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        self.set_status(204)
