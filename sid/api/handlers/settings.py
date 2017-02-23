"""
This module contains handlers which manage settings.
"""

from tornado.web import HTTPError

# Local imports
import sid.api.http as http
import sid.api.auth as auth
from sid.api import __public_key__
from sid.api.handlers.workspace import WorkspaceHandler
from sid.api.macarontower import Catalog
from sid.api.macarontower.exceptions import (
    CatalogNotFoundError,
    UnknownParserTypeError,
    ConfigurationNotFoundError,
    ConfigurationLoadingError,
    SchemaLoadingError,
    ValidationError,
    SchemaError
)

@http.json_error_handling
@http.json_serializer
class SettingsCollectionHandler(WorkspaceHandler):
    """
    This handler process following routes:

        - GET /projects/<project_name>/settings -- List available settings in given project
    """

    def prepare(self, *args, **kwargs):
        """
        Prepare user's workspace and Pyolite configuration to manage projects.
        """
        super(SettingsCollectionHandler, self).prepare()

        # Prepare project into user workspace
        assert self.path_args[0]
        self.project = self.prepare_project(self.path_args[0])

        # Create our macarontower catalog
        try:
            self.catalog = Catalog(self.project.path)
        except CatalogNotFoundError:
            raise HTTPError(
                status_code=503,
                log_message='Failed to read settings catalog. '
                            'Please contact your system administrator.'
            )

    @auth.require_authentication(__public_key__)
    @http.available_content_type(['application/json'])
    def get(self, project_name, *args, **kwargs):
        """
        Get list of available settings.

        Example:
        > GET /projects/example/settings HTTP/1.1
        > Accept: */*
        >
        """
        self.write(self.catalog.list())

@http.json_error_handling
@http.json_serializer
class SettingsHandler(WorkspaceHandler):
    """
    This handler process following routes:

        - GET /projects/<project_name>/settings/<settings_path> -- Get settings from its path
    """

    def prepare(self, *args, **kwargs):
        """
        Prepare user's workspace and Pyolite configuration to manage projects.
        """
        super(SettingsHandler, self).prepare()

        # Prepare project into user workspace
        assert self.path_args[0]
        self.project = self.prepare_project(self.path_args[0])

        # Create our macarontower catalog
        try:
            self.catalog = Catalog(self.project.path)
        except CatalogNotFoundError:
            raise HTTPError(
                status_code=503,
                log_message='Failed to read settings catalog. '
                            'Please contact your system administrator.'
            )

    @auth.require_authentication(__public_key__)
    @http.available_content_type([
        'application/vnd.sid.metadata+json',
        'application/schema+json',
        'application/json'
    ])
    def get(self, project_name, settings_path, *args, **kwargs):
        """
        Get parameter set from its path.

        Example:
        > GET /projects/example/settings/production HTTP/1.1
        > Accept: */*
        >
        """
        output_content_type = kwargs['output_content_type']

        try:
            # User asked JSON data for given settings URI
            if output_content_type == 'application/json':
                self.write(self.catalog.get_data(settings_path))

            # User asked JSON schema for given settings URI
            elif output_content_type == 'application/schema+json':
                self.write(self.catalog.get_schema(settings_path))

            # Return metadata for given settings URI
            elif output_content_type == 'application/vnd.sid.metadata+json':
                self.write(self.catalog.get_metadata(settings_path))

        except UnknownParserTypeError as err:
            raise HTTPError(
                status_code=500,
                log_message='Server side settings error: %s. '
                            'Please contact your system administrator.' % err.message
            )
        except SchemaLoadingError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to load settings schema. '
                            'Please contact your system administrator.'
            )
        except ConfigurationNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Settings \'%s\' not found.' % settings_path
            )
        except ConfigurationLoadingError:
            self.write({})

    @auth.require_authentication(__public_key__)
    @http.available_content_type(['application/json'])
    @http.available_content_type(['application/json'])
    @http.parse_json_body()
    def put(self, project_name, settings_path, *args, **kwargs):
        """
        """
        try:
            # Write data to configuration file using macarontower
            self.catalog.set_data(settings_path, kwargs['json'])

            # Commit all changes made in Git repository
            self.project.commit_all('Modified configuration: %s' % settings_path)

            # Push to remote
            self.project.push('origin')
        except ValidationError as vlde:
            raise HTTPError(
                status_code=400,
                log_message='Configuration error: %s' % vlde.message
            )
        except SchemaError:
            raise HTTPError(
                status_code=500,
                log_message='Invalid JSON schema. '
                            'Please contact your administrator.'
            )
