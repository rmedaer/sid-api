# -*- coding: utf-8 -*-

""" This module contains class which represent a Gitolite configuration
under a Git repository. """

from pyolite2 import Pyolite
from .git_repository import GitRepository

class PyoliteRepository(Pyolite, GitRepository):
    """ A Pyolite configuration under Git repository. """

    def __init__(self, admin_config):
        """ Initialize our Pyolite repository. Open its Git repository. """

        Pyolite.__init__(self, admin_config)
        GitRepository.__init__(self, admin_config)
        # TODO handle "Gitolite repository not found" by remote cloning it

    def save(self, message):
        """ Save Gitolite configuration and commit changes. """

        # Save Gitolite configuration
        Pyolite.save(self)

        # Commit all changes made in Git repository
        self.commit_all(message)
