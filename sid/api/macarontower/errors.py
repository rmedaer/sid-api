from anyconfig import UnknownParserTypeError

class InvalidCatalogError(Exception):
    """
    Error raised when macarontower cannot parse its catalog file.
    """
    pass

class UnknownCatalogVersion(Exception):
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
