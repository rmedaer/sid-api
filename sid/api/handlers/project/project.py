"""
ProjectHandler module (see handler documentation)
"""

import pyolite2
import jsonpatch
from tornado.web import HTTPError
from sid.api import http
from sid.api import auth
from sid.api.handlers.warehouse import AbstractWarehouseHandler
from sid.api.schemas.project import PROJECT_SCHEMA, PROJECT_PATCH_SCHEMA
from sid.lib.warehouse import Warehouse, RepositoryPatchException
from sid.lib.git import ForbiddenException

__projects_prefix__ = 'projects/'

@http.json_error_handling
@http.json_serializer
class ProjectHandler(AbstractWarehouseHandler):
    """
    This handler process following routes:

        - GET    /projects/<project_name> -- Get project information
        - PUT    /projects/<project_name> -- Update a given project
        - DELETE /projects/<project_name> -- Remove a given project
        - PATCH  /projects/<project_name> -- Patch a given project
    """

    @auth.require_authentication()
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
            self.write(self.warehouse.repos[__projects_prefix__ + name])
        except pyolite2.errors.RepositoryNotFoundException:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

    @auth.require_authentication()
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
            repo = self.warehouse.repos[__projects_prefix__ + name]
        except pyolite2.errors.RepositoryNotFoundException:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

        # Generate patch/diff between existing repo and request body
        patches = jsonpatch.make_patch(http.Encoder().default(repo), kwargs['json'])

        # Skip if nothing changed
        if not patches:
            self.write(repo)
            return

        # Patch the diff
        try:
            Warehouse.patch_pyolite_repo(
                repo,
                patches
            )
        except RepositoryPatchException as error:
            raise HTTPError(
                status_code=400,
                log_message=error.message
            )


        # Save Gitolite configuration and commit changes
        try:
            self.warehouse.save('Updated project \'%s\'' % name)
        except ForbiddenException:
            raise HTTPError(
                status_code=403,
                log_message='You are not authorized to update this project\'s configuration'
            )

        # Return updated repository
        self.write(repo)

    @auth.require_authentication()
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
            repo = self.warehouse.repos[__projects_prefix__ + name]
        except pyolite2.errors.RepositoryNotFoundException:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

        # Skip if patch is empty
        if not patches:
            self.write(repo)
            return

        try:
            Warehouse.patch_pyolite_repo(repo, patches)
        except RepositoryPatchException as error:
            raise HTTPError(
                status_code=400,
                log_message=error.message
            )

        try:
            # Save Gitolite configuration and commit changes
            self.warehouse.save('Updated project \'%s\'' % name)
        except ForbiddenException:
            raise HTTPError(
                status_code=403,
                log_message='You are not authorized to patch project\'s configuration'
            )

        # Return updated repository
        self.write(repo)

    @auth.require_authentication()
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
            self.warehouse.repos.remove(__projects_prefix__ + name)
        except pyolite2.errors.RepositoryNotFoundException:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

        try:
            # Save Gitolite configuration and commit changes
            self.warehouse.save('Removed project \'%s\'' % name)
        except ForbiddenException:
            raise HTTPError(
                status_code=403,
                log_message='You are not authorized to remove this project'
            )

        self.set_status(204)

    def data_received(self, *args, **kwargs):
        """
        Implementation of astract data_received.
        """
        pass
