"""
This module contains all exceptions and errors interpreted from remote Gitolite server.
Since smart Git protocol doesn't use standard code, we have to parse message from
Gitolite and try to understand them.

NOTE: An alternative would be to modify Gitolite to return serialized errors
(e.g. JSON, YAML, ...)
"""

import re

FORBIDDEN_PATTERN = '^Remote error: FATAL: \S* any \S* \S* DENIED by fallthru'
HTTP_ERROR = '^Unexpected HTTP status code: (\d*)'

class GitForbidden(Exception):
    """
    Exception raised when user try to push or pull changes and his access has been denied.
    """
    pass

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

class GitAutomaticMergeNotAvailable(Exception):
    """
    Exception raised when user try to automatically merge and it's failed.
    """
    pass

def handle_git_error(error):
    http_matches = re.match(HTTP_ERROR, error.message)
    if http_matches and int(http_matches.group(1)) == 401:
        return GitForbidden()
    elif re.match(FORBIDDEN_PATTERN, error.message):
        return GitForbidden()
    else:
        return error
