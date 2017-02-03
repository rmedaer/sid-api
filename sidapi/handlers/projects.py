# -*- coding: utf-8 -*-

""" Project(s) handlers

This module contains every handlers for project management (list, get, update,
remove, ...)
"""

import json
from jsonschema import validate, ValidationError
from tornado.web import HTTPError
from pyolite2 import RepositoryNotFoundError, RepositoryDuplicateError, Repository
from .error import JsonErrorHandler
from .pyolite import PyoliteHandler
from .content_negociation import NegociatorHandler

POST_PROJECT = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        }
    },
    "required": [
        "name"
    ],
    "additionalProperties": False
}

class WorkspaceHandler(PyoliteHandler, NegociatorHandler):
    """ This handler manage a workspace. """

    def get(self):
        """ List available projects within this workspace. """
        self.negociate_content_type(['application/json'])

        self.write(self.pyolite.repos)

    def post(self):
        self.accepted_content_type(['application/json'])
        self.negociate_content_type(['application/json'])

        try:
            # Parse JSON
            data = json.loads(self.request.body)
            # Validate JSON schema
            validate(data, POST_PROJECT)
            # Create and add repository
            self.pyolite.repos.append(Repository(data['name']))
            # TODO add user permission
            # Save Gitolite configuration
            self.pyolite.save()
        except ValidationError as ve:
            raise HTTPError(
                status_code=400,
                log_message='JSON error: %s' % ve.message
            )
        except RepositoryDuplicateError:
            raise HTTPError(
                status_code=409,
                log_message='Repository \'%s\' already exists' % data['name']
            )
        except ValueError:
            raise HTTPError(
                status_code=400,
                log_message='Unable to parse JSON body.'
            )

class ProjectHandler(PyoliteHandler):

    def get(self, name):
        try:
            self.write(self.pyolite.repos[name])
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Project not found.')
