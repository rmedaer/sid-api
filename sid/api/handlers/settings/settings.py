"""
SettingsHandler module (see handler documentation)
"""

import os
from tornado.web import HTTPError
from whiriho import Whiriho
from whiriho.errors import (
    CatalogNotFoundException,
    CatalogPathException,
    ConfigurationException,
    WhirihoException
)
from sid.api import auth, http
from sid.api.handlers.project import AbstractProjectHandler

__whiriho_catalog__ = 'whiriho.json'

@http.json_error_handling
@http.json_serializer
class SettingsHandler(AbstractProjectHandler):
    """
    This handler process following routes:

        - GET /projects/<project_name>/settings/<settings_path> -- Get settings from its path
    """

    @auth.require_authentication()
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

        self.prepare_project(project_name)

        try:
            whiriho = Whiriho(os.path.join(self.project.path, __whiriho_catalog__))
            whiriho.load()

            # User asked JSON data for given settings URI
            if output_content_type == 'application/json':
                self.write(whiriho.get_config_data(settings_path))

            # User asked JSON schema for given settings URI
            elif output_content_type == 'application/schema+json':
                schema = whiriho.get_config_schema(settings_path)
                if schema is not None:
                    self.write(schema)
                else:
                    # If schema is None, return No content !
                    self.set_status(204)

            # Return metadata for given settings URI
            elif output_content_type == 'application/vnd.sid.metadata+json':
                uri, file_format, schema_uri = whiriho.get_config_meta(settings_path)
                self.write({
                    'uri': uri,
                    'format': file_format,
                    'schema': schema_uri
                })
        except ConfigurationException:
            # If we cannot read configuration, consider it's empty
            self.write({})
        except (CatalogNotFoundException, CatalogPathException):
            # If catalog itself or catalog path given is not found,
            # consider the config doesn't exist
            raise HTTPError(
                status_code=404,
                log_message='Settings \'%s\' not found.' % settings_path
            )
        except WhirihoException as error:
            # Unknown error ..
            raise HTTPError(
                status_code=500,
                log_message='Settings error (%s)' % error.message
            )
