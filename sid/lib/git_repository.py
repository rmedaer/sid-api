# -*- coding: utf-8 -*-

""" Extends features from pygit2 library. """

from pygit2 import Repository, discover_repository # pylint: disable=E0611

class GitRepositoryNotFound(Exception):
    """ Error thrown when Git repository doesn't exist. """
    pass

class GitRepository(Repository):
    """ Inherits pygit2.Repository to implement easier Git methods. """

    def __init__(self, uri):
        """ Initialize a Git Repository. """

        # Discover Git repository under admin_config file
        try:
            Repository.__init__(self, discover_repository(uri))
        except KeyError:
            raise GitRepositoryNotFound()

    def commit_all(self, message, user=None, parents=None):
        """ Commit all files changed. """

        # Use default signature if user is not given
        if not user:
            user = self.default_signature

        # If parents parameters is not specified, use HEAD
        if parents is None:
            parents = [] if self.head_is_unborn else [self.head.target]

        # Read index and add all files
        self.index.read()
        self.index.add_all()

        # Write tree
        tree = self.index.write_tree()

        # Create commit
        self.create_commit(
            'HEAD', # Reference name
            user, user, # Author and committer
            message, # Commit message
            tree, # Commit tree
            parents) # Parent commits

        # Write index
        self.index.write()
