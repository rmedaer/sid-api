"""
Extends features from pygit2 library.
"""

from repository import (
    GitRepository
)
from sid.api.git.errors import (
    GitForbidden,
    GitRepositoryNotFound,
    GitRemoteNotFound,
    GitBranchNotFound,
    GitRemoteDuplicate
)
