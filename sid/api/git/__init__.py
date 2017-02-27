"""
Extends features from pygit2 library.
"""

from sid.api.git.oauth_callback import (
    OAuthCallback
)
from sid.api.git.repository import (
    GitRepository
)
from sid.api.git.errors import (
    GitForbidden,
    GitRepositoryNotFound,
    GitRemoteNotFound,
    GitBranchNotFound,
    GitRemoteDuplicate,
    GitAutomaticMergeNotAvailable
)
