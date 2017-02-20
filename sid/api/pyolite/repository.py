"""
This module contains a class which represent a Gitolite configuration
under a Git repository. Mixing sid.api.git.GitRepository and pyolite2.Pyolite.
"""

import os
import re
from pyolite2 import Pyolite
from sid.api.git import (
    GitRepository,
    GitRepositoryNotFound,
    GitRemoteNotFound,
    GitRemoteDuplicate,
    GitBranchNotFound
)

MAIN_CONFIG = 'conf/gitolite.conf'
REMOTE_NAME = 'origin'

class PyoliteRepository(Pyolite, GitRepository):
    """ A Pyolite configuration under Git repository. """

    def __init__(self, path, origin):
        """ Initialize our Pyolite repository. Open its Git repository. """

        self.origin = origin

        GitRepository.__init__(self, path)
        Pyolite.__init__(self, os.path.join(path, MAIN_CONFIG))

    def load(self):
        # Try to open Git repository
        try:
            GitRepository.open(self)
        except GitRepositoryNotFound:
            GitRepository.initialize(self)

        # Check if remote exists or create it
        try:
            GitRepository.create_remote(self, self.origin, REMOTE_NAME)
        except GitRemoteDuplicate:
            pass

        # Update our local copy
        try:
            self.pull(REMOTE_NAME)
        except GitBranchNotFound:
            raise AssertionError('Remote or local branch not found.')

        # Load Gitolite admin configuration
        Pyolite.load(self)

    def save(self, message):
        """ Save Gitolite configuration and commit changes. """

        # Save Gitolite configuration
        Pyolite.save(self)

        # Commit all changes made in Git repository
        self.commit_all(message)

        # Push to remote
        self.push(REMOTE_NAME)
