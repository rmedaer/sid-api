# -*- coding: utf-8 -*-

""" This module contains handler which manage a project collection
from Gitolite configuration. """

# Global imports
from tornado.web import HTTPError
from pyolite2 import RepositoryDuplicateError, Repository, FileError

# Local imports
from sidapi import __projects_prefix__
from .error import ErrorHandler
from .serializer import SerializerHandler
from sidapi.decorators.content_negociation import negociate_content_type, accepted_content_type
from sidapi.decorators.json_negociation import parse_json_body
from sidapi.helpers import PyoliteRepository, GitRepositoryNotFound
from sidapi.schemas import PROJECT_SCHEMA

class WorkspaceHandler(ErrorHandler, SerializerHandler):
    """ This handler manage a workspace. """

    def initialize(self, admin_config):
        """ Initialize workspace handler. Storing admin_config path. """

        self.pyolite = None
        self.admin_config = admin_config

    def prepare(self):
        """ Prepare handler by instanciating and loading Gitolite configuration. """

        try:
            self.pyolite = PyoliteRepository(self.admin_config)
            self.pyolite.load()
        except (FileError, GitRepositoryNotFound):
            raise HTTPError(
                status_code=503,
                log_message='Projects management temporary unavailable.'
            )

    @negociate_content_type(['application/json'])
    def get(self):
        """ List available projects within this workspace. """

        self.write([project
                    for project in self.pyolite.repos
                    if project.name.startswith(__projects_prefix__)])

    @negociate_content_type(['application/json'])
    @accepted_content_type(['application/json'])
    @parse_json_body(PROJECT_SCHEMA)
    def post(self):
        """ Add a new project in the workspace. """
         # pylint: disable=E1101

        try:
            # Create and add repository
            repo = Repository(__projects_prefix__ + self.json['name'])
            self.pyolite.repos.append(repo)

            # TODO add default user permissions
        except RepositoryDuplicateError:
            raise HTTPError(
                status_code=409,
                log_message='Repository \'%s\' already exists' % self.json['name']
            )

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Created project \'%s\'' % self.json['name'])
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return created repository
        self.write(repo)
