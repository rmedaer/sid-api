"""
This module contains macarontower Catalog class.
"""

import os
import json
import jsonschema
import anyconfig

from . import exceptions
from . import (
    __macarontower_file__,
    __macarontower_schema__,
    __macarontower_schema_1_0_0__
)

class Catalog(object):
    """
    This class abstract reading and writing macarontower file (macarontower.json).
    """

    def __init__(self, path, allow_absolute=False, allow_unsafe=False):
        """
        Catalog constructor.

        Arguments:
        path -- Root directory of the catalog file.
        allow_absolute -- If set, allows to use absolute file path.
        allow_unsafe -- If set, allows to use relative path out of root directory.
        """
        self.path = path
        self.data = None
        self.version = None
        self.allow_absolute = allow_absolute
        self.allow_unsafe = allow_unsafe

        self.open()

    def open(self):
        """
        Open macarontower.json, parse it and validate using schema.
        """
        try:
            with open(os.path.join(self.path, __macarontower_file__), 'r') as fcatalog:
                body = json.loads(fcatalog.read())
                jsonschema.validate(body, __macarontower_schema__)
                self.version = body['version']

                if self.version.startswith('1.'):
                    jsonschema.validate(body, __macarontower_schema_1_0_0__)
                    self.data = body['data']
                else:
                    raise exceptions.UnknownCatalogVersionError()
        except jsonschema.ValidationError as err:
            raise exceptions.CatalogFormatError(err.message)
        except jsonschema.SchemaError:
            raise AssertionError('Error in macarontower schema !')
        except IOError:
            raise exceptions.CatalogNotFoundError()

    def assert_uri(self, uri):
        """
        Assert URI exist or throws a ConfigurationNotFoundError.
        """
        if uri not in self.list():
            raise exceptions.ConfigurationNotFoundError()

    def list(self):
        """
        List known configuration files from the catalog.
        """
        return self.data.keys()

    def get_format(self, uri):
        """
        Get format of given configuration URI.

        Arguments:
        uri -- Configuration path.
        """
        return self.data[uri]['format']

    def get_metadata(self, uri):
        """
        Get metadata about the URI.

        Arguments:
        uri -- URI of configuration.
        """
        self.assert_uri(uri)

        return {
            "title": self.data[uri].get('title'),
            "description": self.data[uri].get('description'),
            "schema": True if self.data[uri].get('schema') else False
        }

    def set_data(self, uri, data):
        """
        Write configuration file after validation.

        Arguments:
        uri -- URI of configuration file.
        data -- Data to set.
        """
        self.assert_uri(uri)

        path = self.safe_path(self.data[uri]['file'])

        # Get schema from URI
        schema = self.get_schema(uri)

        # Validate input data if schema exists
        if schema:
            jsonschema.validate(data, schema)

        # Write well formatted data
        anyconfig.dump(data, path, ac_parser=self.get_format(uri), ac_safe=True)

    def get_data(self, uri):
        """
        Read configuration file from given macarontower URI.

        Arguments:
        uri -- Key from macarontower.json file.
        """
        self.assert_uri(uri)

        path = self.safe_path(self.data[uri]['file'])

        try:
            return anyconfig.load(path, ac_parser=self.get_format(uri))
        except IOError:
            raise exceptions.ConfigurationLoadingError()

    def get_schema(self, uri):
        """
        Read schema for given macarontower URI.

        Arguments:
        uri -- Key from macarontower.json file.
        """
        self.assert_uri(uri)

        if not self.data[uri].get('schema'):
            return {}

        path = self.safe_path(self.data[uri]['schema'])

        try:
            with open(path, 'r') as fschema:
                # TODO after loading schema we should lint it (self-validation)
                return json.loads(fschema.read())
        except IOError:
            raise exceptions.SchemaLoadingError()

    def safe_path(self, path):
        """
        Create safe path from given file with options passed to Catalog object.
        It's using 'allow_unsafe' and 'absolute_path' to refactor input file.

        Arguments:
        path -- Path of file to review.
        """
        # If file has absolute path that we not authorize, raise an error
        if os.path.isabs(path):
            if not self.allow_absolute or not self.allow_unsafe:
                raise AssertionError('Not authorized to load absolute file')
        else:
            path = os.path.join(self.path, path)
            if not os.path.realpath(path).startswith(self.path) and not self.allow_unsafe:
                raise AssertionError('Unsafe path: %s' % path)

        return path
