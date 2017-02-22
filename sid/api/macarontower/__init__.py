"""

"""

import os
import json
import jsonschema
import anyconfig
import errors
import schema

from sid.api.http import is_safe_path

MAIN_FILE = 'macarontower.json'

class Catalog(object):
    def __init__(self, path, allow_absolute=False, allow_unsafe=False):
        self.path = path
        self.data = None
        self.allow_absolute = allow_absolute
        self.allow_unsafe = allow_unsafe

        self.open()

    def open(self):
        """
        Open macarontower.json, parse it and validate using schema.
        """
        try:
            with open(os.path.join(self.path, MAIN_FILE), 'r') as file:
                self.data = json.loads(file.read())
                jsonschema.validate(self.data, schema.MACARONTOWER_SCHEMA)

                if self.data['version'] == '1.0.0':
                    jsonschema.validate(self.data, schema.MACARONTOWER_SCHEMA_1_0_0)
                else:
                    raise errors.UnknownCatalogVersion()
        except jsonschema.ValidationError:
            raise errors.InvalidCatalogError()
        except jsonschema.SchemaError:
            raise AssertionError('Error in macarontower schema !')
        except IOError:
            raise errors.CatalogNotFoundError()

    def assert_uri(self, uri):
        """
        Assert URI exist or throws a ConfigurationNotFoundError.
        """
        if uri not in self.list():
            raise errors.ConfigurationNotFoundError()

    def list(self):
        """
        List known configuration files from the catalog.
        """
        return self.data['configs'].keys()

    def get_format(self, uri):
        """
        Get format of given cconfiguration URI. It also substitutes known format.
        """
        format = self.data['configs'][uri]['format']

        if format == 'yml':
            format = 'yaml'

        return format

    def set_data(self, uri, data):
        """
        Write configuration file after validation.

        Arguments:
        uri -- URI of configuration file.
        data -- Data to set.
        """
        self.assert_uri(uri)

        file = self.safe_path(self.data['configs'][uri]['file'])

        # Get schema from URI
        schema = self.get_schema(uri)

        # Validate input data if schema exists
        if schema:
            jsonschema.validate(data, schema)

        # Write well formatted data
        anyconfig.dump(data, file, ac_parser=self.get_format(uri), ac_safe=True)

    def get_data(self, uri):
        """
        Read configuration file from given macarontower URI.

        Arguments:
        uri -- Key from macarontower.json file.
        """
        self.assert_uri(uri)

        file = self.safe_path(self.data['configs'][uri]['file'])

        try:
            return anyconfig.load(file, ac_parser=self.get_format(uri))
        except IOError as err:
            raise errors.ConfigurationLoadingError()

    def get_schema(self, uri):
        """
        Read schema for given macarontower URI.

        Arguments:
        uri -- Key from macarontower.json file.
        """
        self.assert_uri(uri)

        if not self.data['configs'][uri].get('schema'):
            return {}

        schema = self.safe_path(self.data['configs'][uri]['schema'])

        try:
            with open(schema, 'r') as file:
                # TODO after loading schema we should lint it (self-validation)
                return json.loads(file.read())
        except IOError:
            raise errors.SchemaLoadingError()

    def safe_path(self, file):
        """
        TODO
        """
        # If file has absolute path that we not authorize, raise an error
        if os.path.isabs(file):
            if not self.allow_absolute or not self.allow_unsafe:
                raise AssertionError('Not authorized to load absolute file')
        else:
            file = os.path.join(self.path, file)
            if not is_safe_path(self.path, file) and not self.allow_unsafe:
                raise AssertionError('Unsafe path: %s' % file)

        return file
