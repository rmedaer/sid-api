# -*- coding: utf-8 -*-

""" This module contains class which represent a Gitolite configuration
under a Git repository. """

import os
import re
from pyolite2 import Pyolite
from pygit2 import GitError
from sid.api.git import (
    GitRepository,
    GitRepositoryNotFound,
    GitRemoteNotFound,
    GitRemoteDuplicate
)

MAIN_CONFIG = 'conf/gitolite.conf'
REMOTE_NAME = 'origin'
FORBIDDEN_PATTERN = '^Remote error: FATAL: \S* any \S* \S* DENIED by fallthru'

class GitPushForbidden(Exception):
    """
    Exception raised when user try to push changes and his access has been denied.
    """
    pass

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
        self.pull(REMOTE_NAME)

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

    def push(self, remote_name='origin', branch_name='master'):
        try:
            super(PyoliteRepository, self).push(remote_name, branch_name)
        except GitError as gerr:
            if re.match(FORBIDDEN_PATTERN, gerr.message):
                # Automatically discard changes by fetching changes
                self.reset_hard('refs/remotes/%s/%s' % (remote_name, branch_name))

                raise GitPushForbidden()
            else:
                raise gerr
