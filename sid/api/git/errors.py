"""
This module contains all exceptions and errors interpreted from remote Gitolite server.
Since smart Git protocol doesn't use standard code, we have to parse message from
Gitolite and try to understand them.

NOTE: An alternative would be to modify Gitolite to return serialized errors
(e.g. JSON, YAML, ...)
"""

class GitForbidden(Exception):
    """
    Exception raised when user try to push or pull changes and his access has been denied.
    """
    pass

class GitPushForbidden(GitForbidden):
    """
    Exception raised when user try to push changes and his access has been denied.
    """

class GitPullForbidden(GitForbidden):
    """
    Exception raised when user try to push changes and his access has been denied.
    """

class GitRepositoryNotFound(Exception):
    """
    Exception raised when Git repository doesn't exist.
    """
    pass

class GitRemoteNotFound(Exception):
    """
    Exception raised when Git remote doesn't exist.
    """
    pass

class GitBranchNotFound(Exception):
    """
    Exception raised when Git branch doesn't exist.
    """
    pass

class GitRemoteDuplicate(Exception):
    """
    Exception raised when user try to create a remote which already exists.
    """
    pass
