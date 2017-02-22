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
from sid.api.macarontower.errors import (
    CatalogNotFoundError,
    UnknownParserTypeError,
    ConfigurationNotFoundError,
    ConfigurationLoadingError,
    SchemaLoadingError
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

        # User asked JSON data for given settings URI
        if output_content_type == 'application/json':
            try:
                self.write(self.catalog.get_data(settings_path))
            except UnknownParserTypeError as err:
                raise HTTPError(
                    status_code=500,
                    log_message='Server side settings error: %s. '
                                'Please contact your system administrator.' % err.message
                )
            except ConfigurationNotFoundError as err:
                raise HTTPError(
                    status_code=404,
                    log_message='Settings \'%s\' not found.' % settings_path
                )
            except ConfigurationLoadingError as err:
                self.write({})

        # User asked JSON schema for given settings URI
        elif output_content_type == 'application/schema+json':
            try:
                self.write(self.catalog.get_schema(settings_path))
            except SchemaLoadingError:
                raise HTTPError(
                    status_code=500,
                    log_message='Failed to load settings schema. '
                                'Please contact your system administrator.'
                )

        # We should never be able to come here ...
        else: # pragma: no cover
            raise HTTPError(
                status_code=500,
                log_message='Unrecognized accepted content type: %s' % output_content_type
            )
