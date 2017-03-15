"""
SettingsHandler module (see handler documentation)
"""

import os
import json
import jsonpatch
from tornado.web import HTTPError
from whiriho import Whiriho
from whiriho.errors import (
    CatalogNotFoundException,
    CatalogPathException,
    ConfigurationException,
    ConfigurationSchemaException,
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

        self.prepare_settings(project_name, settings_path)

        try:
            # User asked JSON data for given settings URI
            if output_content_type == 'application/json':
                self.write(self.whiriho.get_config_data(settings_path))

            # User asked JSON schema for given settings URI
            elif output_content_type == 'application/schema+json':
                schema = self.whiriho.get_config_schema(settings_path)
                if schema is not None:
                    self.write(schema)
                else:
                    # If schema is None, return No content !
                    self.set_status(204)

            # Return metadata for given settings URI
            elif output_content_type == 'application/vnd.sid.metadata+json':
                uri, file_format, schema_uri = self.whiriho.get_config_meta(settings_path)
                self.write({
                    'uri': uri,
                    'format': file_format,
                    'schema': schema_uri
                })
        except ConfigurationException:
            # If we cannot read configuration, consider it's empty
            self.write({})


    @auth.require_authentication()
    @http.accepted_content_type(['application/json'])
    @http.available_content_type([
        'application/schema+json',
        'application/json'
    ])
    @http.parse_json_body()
    def put(self, project_name, settings_path, *args, **kwargs):
        """
        Update project settings.

        Arguments:
        _ (project_name) -- Tackled by prepare method.
        settings_path -- Settings to modify.

        Example:
        > PUT /projects/example/settings/production HTTP/1.1
        > Accept: */*
        > Content-Type: application/json
        > Content-Length: ???
        >
        """
        output_content_type = kwargs['output_content_type']
        new_config = kwargs['json']

        self.prepare_settings(project_name, settings_path)

        try:
            old_config = self.whiriho.get_config_data(settings_path)
        except ConfigurationException:
            old_config = {}

        # Generate a list of patch between old and new configuration
        patches = jsonpatch.make_patch(old_config, new_config)

        # If there is something to patch, do it and commit changes
        if patches:
            try:
                self.whiriho.set_config_data(settings_path, new_config)
            except ConfigurationSchemaException as error:
                raise HTTPError(
                    status_code=400,
                    log_message='Invalid data set (%s)' % error.message
                )

            self.project.commit_all(SettingsHandler.format_message(settings_path, patches))

        if output_content_type == 'application/json':
            self.write(new_config)
        elif output_content_type == 'application/schema+json':
            self.set_status(226, reason='IM Used')
            self.write(json.dumps(list(patches)))

    @staticmethod
    def format_message(path, patches):
        """
        Format patch message for Git commit.
        """
        added = []
        replaced = []
        removed = []

        message = 'Modified project settings \'%s\':\n' % path

        for patch in patches:
            if patch['op'] == 'add':
                added.append(patch['path'])
            elif patch['op'] == 'replace':
                replaced.append(patch['path'])
            elif patch['op'] == 'remove':
                removed.append(patch['path'])

        if added:
            message += '  - Added %s\n' % ', '.join(added)
        if replaced:
            message += '  - Replaced %s\n' % ', '.join(replaced)
        if removed:
            message += '  - Removed %s\n' % ', '.join(removed)

        return message

    def prepare_settings(self, project_name, settings_path):
        """
        Prepare settings catalog for given project name.

        Arguments:
        project_name -- Project name.
        """
        self.prepare_project(project_name)

        try:
            self.whiriho = Whiriho(os.path.join(self.project.path, __whiriho_catalog__))
            self.whiriho.load()
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

        return self.whiriho
