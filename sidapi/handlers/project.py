# -*- coding: utf-8 -*-

""" Project(s) handlers

This module contains every handlers for project management.
"""

# Global imports
from tornado.web import HTTPError
from pyolite2 import RepositoryNotFoundError

# Local imports
from .. import __projects_prefix__
from .error import ErrorHandler
from .serializer import SerializerHandler
from .workspace import WorkspaceHandler
from ..decorators import negociate_content_type

class ProjectHandler(WorkspaceHandler, ErrorHandler, SerializerHandler):

    @negociate_content_type(['application/json'])
    def get(self, name):
        try:
            self.write(self.pyolite.repos[__projects_prefix__ + name])
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.'
            )

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
