# -*- coding: utf-8 -*-

from pyolite2 import Pyolite
from .git_repository import GitRepository

class PyoliteRepository(Pyolite, GitRepository):
    def __init__(self, admin_config):
        Pyolite.__init__(self, admin_config)
        GitRepository.__init__(self, admin_config)

    def save(self, message):
        # Save Gitolite configuration
        Pyolite.save(self)

        # Commit all changes made in Git repository
        self.commit_all(message)
