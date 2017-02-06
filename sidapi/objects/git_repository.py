
from pygit2 import Repository, discover_repository

class GitRepositoryNotFound(Exception): pass

class GitRepository(Repository):
    def __init__(self, uri):
        # Discover Git repository under admin_config file
        try:
            Repository.__init__(self, discover_repository(uri))
        except KeyError:
            raise GitRepositoryNotFound()

    def commit_all(self, message, user=None, parents=None):
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
        commit = self.create_commit(
            'HEAD', # Reference name
            user, user, # Author and committer
            message, # Commit message
            tree, # Commit tree
            parents) # Parent commits

        # Write index
        self.index.write()
