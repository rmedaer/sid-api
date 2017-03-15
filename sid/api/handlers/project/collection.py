"""
ProjectCollectionHandler module (see handler documentation).
"""

import pyolite2
import jsonpatch
from tornado.web import HTTPError
from sid.api import http, auth
from sid.api.handlers.warehouse import AbstractWarehouseHandler
from sid.api.schemas.project import PROJECT_SCHEMA
from sid.lib.warehouse import Warehouse, RepositoryPatchException
from sid.lib.git import ForbiddenException

__projects_prefix__ = 'projects/'

@http.json_error_handling
@http.json_serializer
class ProjectCollectionHandler(AbstractWarehouseHandler):
    """
    This handler process following routes:

        - GET  /projects -- List projects
        - POST /projects -- Create a new project
    """

    @http.available_content_type(['application/json'])
    def get(self, *args, **kwargs):
        """
        List all projects.

        Example:
        > GET /projects HTTP/1.1
        > Accept: */*
        >
        """
        self.write([project
                    for project in self.warehouse.repos
                    if project.name.startswith(__projects_prefix__)])

    @auth.require_authentication()
    @http.accepted_content_type(['application/json'])
    @http.available_content_type(['application/json'])
    @http.parse_json_body(PROJECT_SCHEMA)
    def post(self, *args, **kwargs):
        """
        Create and add a new project.

        Example:
        > POST /projects HTTP/1.1
        > Accept: */*
        > Content-Type: application/json
        > Content-Length: 64
        >
        {"name":"test-project","rules":[{"users":["@all"],"perm":"RW"}]}
        """

        try:
            # Create and add repository
            repo = pyolite2.Repository(__projects_prefix__ + kwargs['json']['name'])
            self.warehouse.repos.append(repo)

            # Add user permissions by patching repo
            Warehouse.patch_pyolite_repo(
                repo,
                jsonpatch.make_patch(
                    http.Encoder().default(repo),
                    kwargs['json']
                )
            )
        except pyolite2.errors.RepositoryDuplicateException:
            raise HTTPError(
                status_code=409,
                log_message='Repository \'%s\' already exists' % kwargs['json']['name']
            )
        except RepositoryPatchException as error:
            raise HTTPError(
                status_code=400,
                log_message=error.message
            )

        try:
            # Save Gitolite configuration and commit changes
            self.warehouse.save('Created project \'%s\'' % kwargs['json']['name'])
        except ForbiddenException:
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

    def data_received(self, *args, **kwargs):
        """
        Implementation of astract data_received.
        """
        pass
