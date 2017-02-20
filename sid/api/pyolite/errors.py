"""
This module contains all exceptions and errors interpreted from remote Gitolite server.
Since smart Git protocol doesn't use standard code, we have to parse message from
Gitolite and try to understand them.

NOTE: An alternative would be to modify Gitolite to return serialized errors
(e.g. JSON, YAML, ...)
"""

class GitPushForbidden(Exception):
    """
    Exception raised when user try to push changes and his access has been denied.
    """
    pass
