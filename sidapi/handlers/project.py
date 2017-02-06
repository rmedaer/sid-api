# -*- coding: utf-8 -*-

""" Project(s) handlers

This module contains every handlers for project management.
"""

# Global imports
from tornado.web import HTTPError
from pyolite2 import RepositoryNotFoundError

# Local imports
from .error import ErrorHandler
from .serializer import SerializerHandler
from ..decorators import negociate_content_type

class ProjectHandler(ErrorHandler, SerializerHandler):

    @negociate_content_type(['application/json'])
    def get(self, name):
        try:
            self.write(self.pyolite.repos[name])
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.')
