"""
This module contains GitRepository class. It exposes usual commands on Git
repository with pygit2 library.
"""

import re
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
    GitPushForbidden,
    GitPullForbidden,
    GitRepositoryNotFound,
    GitRemoteNotFound,
    GitBranchNotFound,
    GitRemoteDuplicate
)

FORBIDDEN_PATTERN = '^Remote error: FATAL: \S* any \S* \S* DENIED by fallthru'

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

    def add_file(self, file):
        """
        Add given file to current index.

        Keyword arguments:
        file -- A string which contains relative path of file to add.
        """
        assert self.is_open()

        self.repo.index.add(self.resolve_path(file))
        self.repo.index.write()

    def add_files(self, files):
        """
        Add given files to current index.

        Keyword arguments:
        files -- An array of string which contains files to add
        """
        for file in files:
            self.add_file(file)

    def commit(self, message, user=None, parents=None):
        """
        Commit changes.

        Keyword arguments:
        message -- Commit message.
        user -- Commit user (default: default_signature)
        parents -- Parent commits (default: HEAD)
        """
        assert self.is_open()

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

    def create_remote(self, url, name='origin'):
        """
        Create a remote using given url.self.lookup_branch(branch_name)
        url -- Remote URL.
        name -- Remote name (default: 'origin')
        """
        assert self.is_open()

        try:
            return self.repo.create_remote(name, url)
        except ValueError:
            raise GitRemoteDuplicate()

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

    def pull(self, remote_name, branch_name='master'):
        """
        Pull changes from given remote repository.

        Keyword arguments:
        remote_name -- Name of remote to pull.
        branch_name -- Name of remote branch to pull.
        """
        assert self.is_open()

        # Retrieve and fetch remote
        remote = self.get_remote(remote_name)
        try:
            remote.fetch(callbacks=self.callbacks)
        except GitError as gerr:
            if re.match(FORBIDDEN_PATTERN, gerr.message):
                raise GitPullForbidden()
            else:
                raise gerr

        # Lookup remote reference, oid and commit
        remote_ref = 'refs/remotes/%s/%s' % (remote_name, branch_name)
        try:
            remote_oid = self.repo.lookup_reference(remote_ref).target
            remote_commit = self.repo.get(remote_oid)
        except KeyError:
            raise GitBranchNotFound()

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
            raise AssertionError('Unable to do merge')

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
            if re.match(FORBIDDEN_PATTERN, gerr.message):
                # Automatically discard changes by fetching changes
                self.reset_hard('refs/remotes/%s/%s' % (remote_name, branch_name))

                raise GitPushForbidden()
            else:
                raise gerr

    def set_callbacks(self, callbacks):
        """
        Set repository callbacks: authentication, progress, ...
        """

        self.callbacks = callbacks

    def resolve_path(self, file):
        """
        Resolve file to relative Git path.

        Keyword arguments:
        file -- Path to be resolved
        """
        assert self.is_open()

        if os.path.isabs(file):
            return os.path.relative(file, self.repo.workdir)
        else:
            return file

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
