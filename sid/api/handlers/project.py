"""
Project(s) handlers
This module contains every handlers for project management.
"""

# Global imports
from jsonpatch import make_patch
from tornado.web import HTTPError
from pyolite2 import RepositoryNotFoundError

# Local imports
from sid.api import __projects_prefix__, __public_key__
from sid.api.auth import require_authentication
from sid.api.handlers.error import ErrorHandler
from sid.api.handlers.serializer import SerializerHandler
from sid.api.handlers.pyolite import PyoliteHandler
from sid.api.http import available_content_type, accepted_content_type, parse_json_body
from sid.api.schemas import PROJECT_SCHEMA, PROJECT_PATCH_SCHEMA
from sid.lib import PyoliteEncoder, patch_repo

class ProjectHandler(PyoliteHandler, ErrorHandler, SerializerHandler):
    """ Project handler """

    @require_authentication(__public_key__)
    @available_content_type(['application/json'])
    def get(self, name, *args, **kwargs):
        try:
            self.write(self.pyolite.repos[__projects_prefix__ + name])
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

    @require_authentication(__public_key__)
    @available_content_type(['application/json'])
    @accepted_content_type(['application/json'])
    @parse_json_body(PROJECT_SCHEMA)
    def put(self, name, *args, **kwargs):
        try:
            repo = self.pyolite.repos[__projects_prefix__ + name]
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

        patch_repo(repo, make_patch(PyoliteEncoder().default(repo), kwargs['json']))

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Updated project \'%s\'' % name)
        except GitPushForbidden:
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

    @require_authentication(__public_key__)
    @available_content_type(['application/json'])
    @accepted_content_type(['application/json'])
    @parse_json_body(PROJECT_PATCH_SCHEMA)
    def patch(self, name, *args, **kwargs):
        try:
            repo = self.pyolite.repos[__projects_prefix__ + name]
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

        patch_repo(repo, kwargs['json'])

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Updated project \'%s\'' % name)
        except GitPushForbidden:
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

    @require_authentication(__public_key__)
    def delete(self, name, *args, **kwargs):
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
        except GitPushForbidden:
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
