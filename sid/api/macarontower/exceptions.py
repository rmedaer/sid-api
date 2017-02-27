"""
This module contains exceptions raised by macarontower module.
"""

# The following imports are there to help development. It's a kind of symlink
# of known errors from anyconfig and jsonschema modules.
# pylint: disable=W0611
from anyconfig import UnknownParserTypeError
from jsonschema import ValidationError, SchemaError

class CatalogFormatError(Exception):
    """
    Error raised when macarontower cannot parse its catalog file.
    """
    pass

class UnknownCatalogVersionError(Exception):
    """
    Error raised when catalog version is not recognized by macarontower.
    """
    pass

class CatalogNotFoundError(Exception):
    """
    Error raised when catalog cannot be loaded.
    """
    pass

class ConfigurationNotFoundError(Exception):
    """
    Error raised when given URI doesn't exist in catalog.
    """
    pass

class ConfigurationLoadingError(Exception):
    """
    Error raised when macarontower cannot load a configuration file.
    """
    pass

class SchemaLoadingError(Exception):
    """
    Error raised when macarontower cannot load a schema file.
    """
    pass
