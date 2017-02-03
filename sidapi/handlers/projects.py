# -*- coding: utf-8 -*-

""" Project(s) handlers

This module contains every handlers for project management (list, get, update,
remove, ...)
"""

from tornado.web import HTTPError
from pyolite2 import RepositoryNotFoundError
from .error import JsonErrorHandler
from .pyolite import PyoliteHandler

class WorkspaceHandler(PyoliteHandler, JsonErrorHandler):
    """ This handler manage a workspace. """

    def initialize(self, pyolite):
        # Store pyolite configuration
        self.pyolite = pyolite

    def get(self):
        """ List available projects within this workspace. """
        self.write(self.pyolite.repos)

    # TODO implement POST

class ProjectHandler(PyoliteHandler, JsonErrorHandler):

    def initialize(self, pyolite):
        self.pyolite = pyolite

    def get(self, name):
        try:
            self.write(self.pyolite.repos[name])
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.')
