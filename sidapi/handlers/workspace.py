# -*- coding: utf-8 -*-

""" This module contains handler which manage a project collection
from Gitolite configuration. """

# Global imports
from tornado.web import HTTPError
from pyolite2 import RepositoryDuplicateError, Repository

# Local imports
from sidapi import __projects_prefix__
from sidapi.handlers.error import ErrorHandler
from sidapi.handlers.serializer import SerializerHandler
from sidapi.handlers.pyolite import PyoliteHandler
from sidapi.decorators.content_negociation import available_content_type, accepted_content_type
from sidapi.decorators.json_negociation import parse_json_body
from sidapi.schemas import PROJECT_SCHEMA

class WorkspaceHandler(PyoliteHandler, ErrorHandler, SerializerHandler):
    """ This handler manage a workspace. """

    @available_content_type(['application/json'])
    def get(self, *args, **kwargs):
        """ List available projects within this workspace. """

        self.write([project
                    for project in self.pyolite.repos
                    if project.name.startswith(__projects_prefix__)])

    @accepted_content_type(['application/json'])
    @available_content_type(['application/json'])
    @parse_json_body(PROJECT_SCHEMA)
    def post(self, *args, **kwargs):
        """ Add a new project in the workspace. """

        try:
            # Create and add repository
            repo = Repository(__projects_prefix__ + kwargs['json']['name'])
            self.pyolite.repos.append(repo)

            # TODO add default user permissions
        except RepositoryDuplicateError:
            raise HTTPError(
                status_code=409,
                log_message='Repository \'%s\' already exists' % kwargs['json']['name']
            )

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Created project \'%s\'' % kwargs['json']['name'])
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return created repository
        self.write(repo)
