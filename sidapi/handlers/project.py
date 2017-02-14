# -*- coding: utf-8 -*-

""" Project(s) handlers

This module contains every handlers for project management.
"""

# Global imports
from jsonpatch import make_patch
from tornado.web import HTTPError
from pyolite2 import RepositoryNotFoundError

# Local imports
from .. import __projects_prefix__
from .error import ErrorHandler
from .serializer import SerializerHandler
from .workspace import WorkspaceHandler
from ..helpers import PyoliteEncoder, patch_repo
from sidapi.decorators.content_negociation import negociate_content_type, accepted_content_type
from sidapi.decorators.json_negociation import parse_json_body
from ..schemas import PROJECT_SCHEMA, PROJECT_PATCH_SCHEMA

class ProjectHandler(WorkspaceHandler, ErrorHandler, SerializerHandler):
    """ Project handler """

    @negociate_content_type(['application/json'])
    def get(self, name):
        try:
            self.write(self.pyolite.repos[__projects_prefix__ + name])
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

    @negociate_content_type(['application/json'])
    @accepted_content_type(['application/json'])
    @parse_json_body(PROJECT_SCHEMA)
    def put(self, name):
        try:
            repo = self.pyolite.repos[__projects_prefix__ + name]
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

        patch_repo(repo, make_patch(PyoliteEncoder().default(repo), self.json)) # pylint: disable=E1101

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Updated project \'%s\'' % name)
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return updated repository
        self.write(repo)

    @negociate_content_type(['application/json'])
    @accepted_content_type(['application/json'])
    @parse_json_body(PROJECT_PATCH_SCHEMA)
    def patch(self, name):
        try:
            repo = self.pyolite.repos[__projects_prefix__ + name]
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

        patch_repo(repo, self.json) # pylint: disable=E1101

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Updated project \'%s\'' % name)
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return updated repository
        self.write(repo)

    def delete(self, name):
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
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        self.set_status(204)
