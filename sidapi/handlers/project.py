# -*- coding: utf-8 -*-

""" Project(s) handlers

This module contains every handlers for project management.
"""

# Global imports
from jsonpatch import make_patch
from tornado.web import HTTPError
from pyolite2 import RepositoryNotFoundError

# Local imports
from sidapi import __projects_prefix__
from sidapi.handlers.error import ErrorHandler
from sidapi.handlers.serializer import SerializerHandler
from sidapi.handlers.pyolite import PyoliteHandler
from sidapi.helpers import PyoliteEncoder, patch_repo
from sidapi.decorators.content_negociation import available_content_type, accepted_content_type
from sidapi.decorators.json_negociation import parse_json_body
from sidapi.schemas import PROJECT_SCHEMA, PROJECT_PATCH_SCHEMA

class ProjectHandler(PyoliteHandler, ErrorHandler, SerializerHandler):
    """ Project handler """

    @available_content_type(['application/json'])
    def get(self, name, *args, **kwargs):
        try:
            self.write(self.pyolite.repos[__projects_prefix__ + name])
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

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
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return updated repository
        self.write(repo)

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
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return updated repository
        self.write(repo)

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
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        self.set_status(204)
