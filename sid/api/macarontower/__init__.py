"""
Macarontower is a library which manage and maintain a catalog of configuration
files and their schemas.
"""

from sid.api.macarontower.catalog import Catalog
from sid.api.macarontower.exceptions import (
    UnknownParserTypeError, # from anyconfig
    ValidationError, SchemaError, # from jsonschema
    CatalogFormatError,
    UnknownCatalogVersionError,
    CatalogNotFoundError,
    ConfigurationNotFoundError,
    ConfigurationLoadingError,
    SchemaLoadingError
)

__macarontower_file__ = 'macarontower.json'
__macarontower_schema__ = {
    "type": "object",
    "properties": {
        "version": {
            "type": "string",
            "pattern": r"^\d*\.\d*\.\d*$"
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
            "pattern": r"^\d*\.\d*\.\d*$"
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
                    },
                    "title": {
                        "type": "string"
                    },
                    "description": {
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
