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

class PyoliteRepository(Pyolite, GitRepository):
    """ A Pyolite configuration under Git repository. """

    def __init__(self, path):
        """ Initialize our Pyolite repository. Open its Git repository. """
        GitRepository.__init__(self, path)
        Pyolite.__init__(self, os.path.join(path, MAIN_CONFIG))

    def load(self):
        # Load Gitolite admin configuration
        Pyolite.load(self)

    def save(self, message, remote='origin'):
        """ Save Gitolite configuration and commit changes. """

        # Save Gitolite configuration
        Pyolite.save(self)

        # Commit all changes made in Git repository
        self.commit_all(message)

        # Push to remote
        self.push(remote)
