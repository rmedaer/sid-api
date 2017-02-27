"""
This module contains GitRepository class. It exposes usual commands on Git
repository with pygit2 library.
"""

import os
from pygit2 import ( # pylint: disable=E0611
    Repository,
    GitError,
    discover_repository,
    init_repository,
    GIT_MERGE_ANALYSIS_UP_TO_DATE,
    GIT_MERGE_ANALYSIS_FASTFORWARD,
    GIT_MERGE_ANALYSIS_NORMAL,
    GIT_RESET_HARD
)
from sid.api.git.errors import (
    GitForbidden,
    GitRepositoryNotFound,
    GitRemoteNotFound,
    GitBranchNotFound,
    GitAutomaticMergeNotAvailable,
    handle_git_error
)

class GitRepository(object):
    """
    Represents a Git repository from higher level then pygit2.
    """

    def __init__(self, path):
        """
        Construct a Git Repository.

        Keyword arguments:
        path -- the repository path
        """
        self.repo = None
        self.path = path
        self.callbacks = None

    def initialize(self):
        """
        Initializing Git repository.
        """
        self.repo = init_repository(self.path)

    def open(self):
        """
        Open this Git repository.
        """
        try:
            self.repo = Repository(discover_repository(self.path))
        except KeyError:
            raise GitRepositoryNotFound()

    def add_file(self, path):
        """
        Add given file to current index.

        Keyword arguments:
        path -- A string which contains relative path of file to add.
        """
        assert self.is_open()

        self.repo.index.add(self.resolve_path(path))
        self.repo.index.write()

    def add_files(self, paths):
        """
        Add given files to current index.

        Keyword arguments:
        paths -- An array of string which contains files to add
        """
        for path in paths:
            self.add_file(path)

    def commit(self, message, user=None, parents=None, allow_empty=False): # pylint: disable=W0613
        """
        Commit changes.

        Keyword arguments:
        message -- Commit message.
        user -- Commit user (default: default_signature)
        parents -- Parent commits (default: HEAD)
        """
        assert self.is_open()

        # TODO Make sure we have something to commit if allow_empty is False
        #      Don't forget to remove pylint exception W0613

        # Use default signature if user is not given
        if user is None:
            user = self.repo.default_signature

        # If parents parameters is not specified, use HEAD
        if parents is None:
            parents = [] if self.repo.head_is_unborn else [self.repo.head.target]

        # Write tree
        tree = self.repo.index.write_tree()

        # Create commit
        self.repo.create_commit(
            'HEAD', # Reference name
            user, user, # Author and committer
            message, # Commit message
            tree, # Commit tree
            parents) # Parent commits

    def commit_all(self, message, user=None, parents=None):
        """
        Commit all changes. (see #commit())
        """
        assert self.is_open()

        # Add all files
        self.repo.index.add_all()
        self.repo.index.write()

        self.commit(message, user=user, parents=parents)

    def get_remote(self, remote_name):
        """
        Get Remote object from given name.

        Keyword arguments:
        remote_name -- Name of remote to retrieve.

        Throws GitRemoteNotFound: when remote doesn't exist.
        """
        assert self.is_open()

        try:
            return self.repo.remotes[remote_name]
        except KeyError:
            raise GitRemoteNotFound()

    def set_remote(self, url, name='origin'):
        """
        Set a remote using given url.

        Arguments:
        url -- Remote URL.
        name -- Remote name (default: 'origin')
        """
        assert self.is_open()

        try:
            return self.repo.remotes.create(name, url)
        except ValueError:
            self.repo.remotes.set_url(name, url)

    def get_branch(self, branch_name):
        """
        Get branch from its name.
        """
        assert self.is_open()

        branch = self.repo.lookup_branch(branch_name)

        if not branch:
            raise GitBranchNotFound()

        return branch

    def create_branch(self, branch_name, commit):
        """
        Create new branch based on given commit.
        """
        return self.repo.create_branch(branch_name, commit)

    def fetch_all(self, remote_name):
        """
        Fetch changes from given remote.

        Arguments:
        remote_name -- Remote name.
        """
        assert self.is_open()

        remote = self.get_remote(remote_name)
        try:
            remote.fetch(callbacks=self.callbacks)
        except GitError as gerr:
            raise handle_git_error(gerr)

        return remote # almost useful to return fetched remote

    def pull(self, remote_name, branch_name='master'):
        """
        Pull changes from given remote repository.

        Keyword arguments:
        remote_name -- Name of remote to pull.
        branch_name -- Name of remote branch to pull.
        """
        assert self.is_open()

        # Retrieve and fetch remote
        self.fetch_all(remote_name)

        # Lookup remote reference, oid and commit
        remote_ref = 'refs/remotes/%s/%s' % (remote_name, branch_name)
        try:
            remote_oid = self.repo.lookup_reference(remote_ref).target
            remote_commit = self.repo.get(remote_oid)
        except KeyError:
            # Remote branch doesn't exist; this is the case on new repository,
            # ignore the error
            return

        # Analyze which kind of merge we have to do during the pull
        merge_result, _ = self.repo.merge_analysis(remote_oid)

        # Up to date, nothing to do
        if merge_result & GIT_MERGE_ANALYSIS_UP_TO_DATE:
            pass

        # Handle fastforward: checkout + set current branch
        elif merge_result & GIT_MERGE_ANALYSIS_FASTFORWARD:
            # Check out tree from remote commit
            self.repo.checkout_tree(remote_commit)

            try:
                local_branch = self.get_branch(branch_name)
            except GitBranchNotFound:
                local_branch = self.create_branch(branch_name, remote_commit)

            local_branch.set_target(remote_oid)

            # Set HEAD
            self.repo.set_head(local_branch.name)

        # NOTE: We currently NOT support merge during pull.
        elif merge_result & GIT_MERGE_ANALYSIS_NORMAL:
            raise GitAutomaticMergeNotAvailable('Merge when pulling is not implemented')

        else:
            raise AssertionError('Unknown merge analysis result')

    def push(self, remote_name='origin', branch_name='master'):
        """
        Push changes to given remote.

        Keyword arguments:
        remote_name -- Remote to be pushed.
        branch_name -- Branch to be pushed.
        """
        remote = self.get_remote(remote_name)
        try:
            remote.push([self.get_branch(branch_name).name], callbacks=self.callbacks)
        except GitError as gerr:
            err = handle_git_error(gerr)

            if isinstance(gerr, GitForbidden):
                # Automatically discard changes by fetching changes
                self.reset_hard('refs/remotes/%s/%s' % (remote_name, branch_name))

            raise err

    def set_callbacks(self, callbacks):
        """
        Set repository callbacks: authentication, progress, ...
        """

        self.callbacks = callbacks

    def resolve_path(self, path):
        """
        Resolve file to relative Git path.

        Keyword arguments:
        path -- Path to be resolved
        """
        assert self.is_open()

        if os.path.isabs(path):
            return os.path.relpath(path, self.repo.workdir)
        else:
            return path

    def reset_hard(self, oid):
        """
        Reset repository to given OID.

        Keyword arguments:
        oid -- Targeted OID.
        """
        assert self.is_open()

        if isinstance(oid, basestring):
            oid = self.repo.lookup_reference(oid).target

        self.repo.reset(oid, GIT_RESET_HARD)

    def is_open(self):
        """
        Return a boolean which define if repository is open or not.
        """
        return self.repo is not None

    def ahead_behind(self, remote_name='origin', branch_name='master'):
        """
        Calculate how many different commits are in the non-common parts of
        the history between the two given ids.

        Arguments:
        remote_name -- Targeted remote (optional, default='origin')
        branch_name -- Remote branch (optional, default='origin')
        """
        assert self.is_open()

        # First fetch changes from remote
        self.fetch_all(remote_name)

        # Calculate diff
        return self.repo.ahead_behind(
            self.repo.revparse_single('HEAD').id,
            self.repo.revparse_single('refs/remotes/%s/%s' % (remote_name, branch_name)).id
        )
