"""
Macarontower is a library which manage and maintain a catalog of configuration
files and their schemas.
"""

__macarontower_file__ = 'macarontower.json'
__macarontower_schema__ = {
    "type": "object",
    "properties": {
        "version": {
            "type": "string",
            "pattern": "^\d*\.\d*\.\d*$"
        }
    },
    "required": [
        "version"
    ],
    "additionalProperties": True
}
__macarontower_schema_1_0_0__ = {
    "type": "object",
    "properties": {
        "version": {
            "type": "string",
            "pattern": "^\d*\.\d*\.\d*$"
        },
        "data": {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string"
                    },
                    "format": {
                        "enum": ["yaml", "json", "ini"]
                    },
                    "schema": {
                        "type": "string"
                    }
                },
                "required": [
                    "file",
                    "format"
                ]
            }
        }
    },
    "required": [
        "version",
        "data"
    ],
    "additionalProperties": False
}

from catalog import Catalog
from exceptions import (
    UnknownParserTypeError, # from anyconfig
    ValidationError, SchemaError, # from jsonschema
    CatalogFormatError,
    UnknownCatalogVersionError,
    CatalogNotFoundError,
    ConfigurationNotFoundError,
    ConfigurationLoadingError,
    SchemaLoadingError
)
