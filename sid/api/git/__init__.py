"""
Extends features from pygit2 library.
"""

from repository import (
    GitRepository
)
from sid.api.git.errors import (
    GitForbidden,
    GitPushForbidden,
    GitPullForbidden,
    GitRepositoryNotFound,
    GitRemoteNotFound,
    GitBranchNotFound,
    GitRemoteDuplicate
)
