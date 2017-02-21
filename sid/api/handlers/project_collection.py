"""
This module contains handler which manage a project collection
from Gitolite configuration.
"""

# Global imports
from jsonpatch import make_patch
from tornado.web import HTTPError
from pyolite2 import RepositoryDuplicateError, Repository

# Local imports
from sid.api import __projects_prefix__, __public_key__
from sid.api.auth import require_authentication
from sid.api.handlers.error import ErrorHandler
from sid.api.handlers.serializer import SerializerHandler
from sid.api.handlers.pyolite import PyoliteHandler
from sid.api.http import available_content_type, accepted_content_type, parse_json_body
from sid.api.schemas import PROJECT_SCHEMA
from sid.api.pyolite import PyoliteEncoder, patch_pyolite_repo
from sid.api.git import GitForbidden

class ProjectCollectionHandler(PyoliteHandler, ErrorHandler, SerializerHandler):
    """ This handler manage a workspace. """

    @require_authentication(__public_key__)
    @available_content_type(['application/json'])
    def get(self, *args, **kwargs):
        """ List available projects within this workspace. """

        self.write([project
                    for project in self.pyolite.repos
                    if project.name.startswith(__projects_prefix__)])

    @require_authentication(__public_key__)
    @accepted_content_type(['application/json'])
    @available_content_type(['application/json'])
    @parse_json_body(PROJECT_SCHEMA)
    def post(self, *args, **kwargs):
        """ Add a new project in the workspace. """

        try:
            # Create and add repository
            repo = Repository(__projects_prefix__ + kwargs['json']['name'])
            self.pyolite.repos.append(repo)

            # Add user permissions
            patch_pyolite_repo(repo, make_patch(PyoliteEncoder().default(repo), kwargs['json']))
        except RepositoryDuplicateError:
            raise HTTPError(
                status_code=409,
                log_message='Repository \'%s\' already exists' % kwargs['json']['name']
            )

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Created project \'%s\'' % kwargs['json']['name'])
        except GitForbidden:
            raise HTTPError(
                status_code=403,
                log_message='You are not authorized to create projects'
            )
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return created repository
        self.write(repo)
