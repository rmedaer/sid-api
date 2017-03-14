"""
This module contains helper classes and functions to manipulate Git repositories.
"""


import os
import re
import pygit2

__forbidden_pattern__ = r'^Remote error: FATAL: \S* any \S* \S* DENIED by fallthru'
__http_error__ = r'^Unexpected HTTP status code: (\d*)'

class RepositoryNotFoundException(Exception):
    """
    Exception raised when repository could not be found.
    """
    pass

class ForbiddenException(Exception):
    """
    Exception raised when we detect a forbidden from Gitolite.
    """
    pass

class BranchNotFoundException(Exception):
    """
    Exception raised when branch could not be found.
    """
    pass

class RemoteNotFoundException(Exception):
    """
    Exception raised when remote could not be found.
    """
    pass

class SignatureException(Exception):
    """
    Exception raised when not any signature found.
    """
    pass

class GitAutomaticMergeNotAvailable(Exception):
    """
    Exception raised when we cannot automatically merge.
    """
    pass

class OAuthCallback(pygit2.RemoteCallbacks):
    """
    Abstract OAuth mechanism for SID warehouse.
    """

    def __init__(self, user, token):
        """
        Construct a OAuthCallback.
        """
        super(OAuthCallback, self).__init__()

        self.user = user
        self.token = token

    def credentials(self, url, username_from_url, allowed_types): # pylint: disable=E0202
        """
        Return credentials as UserPass object. Instead of putting "real" password
        it's using OAuth token.
        """
        return pygit2.UserPass(self.user, self.token)

class Repository(object):# pylint: disable=R0904
    """
    Easy Git repository class.
    It represents a repository from higher level then pygit2.
    """

    def __init__(self, path):
        """
        Construct a Git repository object.

        Arguments:
        path -- Repository path.
        """
        self.repo = None
        self.sign = None
        self.path = path
        self.callbacks = None

    def initialize(self):
        """
        Initialize the Git repository.
        """
        self.repo = pygit2.init_repository(self.path)

    def open(self):
        """
        Open the Git repository.
        """
        try:
            self.repo = pygit2.Repository(pygit2.discover_repository(self.path)) # pylint: disable=E1101
        except KeyError:
            raise RepositoryNotFoundException('Could not found repository')

    def is_open(self):
        """
        Return a boolean which define if repository has been opened or not.
        """
        return self.repo is not None

    def assert_is_open(self):
        """
        Assert this repository has been opened or not.
        """
        assert self.is_open(), 'please first open the repository'

    def resolve_path(self, path):
        """
        Resolve file path to relative Git path.

        Arguments:
        path -- Path to be resolved
        """
        self.assert_is_open()

        if os.path.isabs(path):
            return os.path.relpath(path, self.repo.workdir)
        else:
            return path

    def add_file(self, path):
        """
        Add given file to current index.

        Arguments:
        path -- Relative path of file to be added.
        """
        self.assert_is_open()

        self.repo.index.add(self.resolve_path(path))
        self.repo.index.write()

    def add_files(self, paths):
        """
        Add given files to current index.

        Arguments:
        paths -- An array of string which contains files to add
        """
        for path in paths:
            self.add_file(path)

    def commit(self, message, user=None, parents=None, allow_empty=False): # pylint: disable=W0613
        """
        Commit changes.

        Arguments:
        message -- Commit message.
        user -- Commit user (default: default_signature)
        parents -- Parent commits (default: HEAD)
        allow_empty -- TODO
        """
        assert self.is_open()

        # TODO Make sure we have something to commit if allow_empty is False
        #      Don't forget to remove pylint exception W0613

        # Use default signature if user is not given
        if user is None:
            user = self.sign if self.sign else self.get_default_signature()

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
        Commit all changes. (see Repository#commit())
        """
        assert self.is_open()

        # Add all files
        self.repo.index.add_all()
        self.repo.index.write()

        self.commit(message, user=user, parents=parents)

    def get_default_signature(self):
        """
        Return default signature.

        Raises:
        SignatureException if not any signature found.
        """
        try:
            self.repo.default_signature
        except KeyError as error:
            raise SignatureException(error.message)

    def set_default_signature(self, username, email):
        """
        Set default repository signature.

        Arguments:
        username -- Author username.
        email -- Author email.
        """
        self.sign = pygit2.Signature(username, email) # pylint: disable=E1101

    def get_remote(self, remote_name):
        """
        Get Remote object from given name.

        Arguments:
        remote_name -- Name of remote to retrieve.

        Raises:
        GitException; when remote doesn't exist.
        """
        self.assert_is_open()

        try:
            return self.repo.remotes[remote_name]
        except KeyError:
            raise RemoteNotFoundException('Remote \'%s\' not found' % remote_name)

    def set_remote(self, url, name='origin'):
        """
        Set a remote using given url.

        Arguments:
        url -- Remote URL.
        name -- Remote name (default: 'origin')
        """
        self.assert_is_open()

        try:
            return self.repo.remotes.create(name, url)
        except ValueError:
            self.repo.remotes.set_url(name, url)

    def set_callbacks(self, callbacks):
        """
        Set repository callbacks for authentication, progress, ...

        Arguments:
        callbacks -- Repository callback object.
        """
        self.callbacks = callbacks

    def create_branch(self, branch_name, commit):
        """
        Create new branch based on given commit.

        Arguments:
        branch_name -- Branch name.
        commit -- Commit object which will be referenced by the branch.
        """
        self.assert_is_open()
        return self.repo.create_branch(branch_name, commit)

    def get_branch(self, branch_name):
        """
        Get branch from its name.

        Arguments:
        branch_name -- Branch name
        """
        self.assert_is_open()

        branch = self.repo.lookup_branch(branch_name)

        if not branch:
            raise BranchNotFoundException('Branch \'%s\' not found' % branch_name)

        return branch

    def fetch_all(self, remote_name):
        """
        Fetch changes from given remote.

        Arguments:
        remote_name -- Remote name.
        """
        self.assert_is_open()

        remote = self.get_remote(remote_name)
        try:
            remote.fetch(callbacks=self.callbacks)
        except pygit2.GitError as git_error: # pylint: disable=E1101
            raise Repository.handle_git_error(git_error)

        return remote # almost useful to return fetched remote

    def pull(self, remote_name, branch_name='master'):
        """
        Pull changes from given remote repository.

        Arguments:
        remote_name -- Name of remote to pull.
        branch_name -- Name of remote branch to pull.
        """
        self.assert_is_open()

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
        if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE: # pylint: disable=E1101
            pass

            # Handle fastforward: checkout + set current branch
        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD: # pylint: disable=E1101
            # Check out tree from remote commit
            self.repo.checkout_tree(remote_commit)

            try:
                local_branch = self.get_branch(branch_name)
            except BranchNotFoundException:
                local_branch = self.create_branch(branch_name, remote_commit)

            local_branch.set_target(remote_oid)

            # Set HEAD
            self.repo.set_head(local_branch.name)

        # NOTE: We currently NOT support merge during pull.
        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL: # pylint: disable=E1101
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
        except pygit2.GitError as git_error: # pylint: disable=E1101
            err = Repository.handle_git_error(git_error)

            if isinstance(git_error, ForbiddenException):
                # Automatically discard changes by fetching changes
                self.reset_hard('refs/remotes/%s/%s' % (remote_name, branch_name))

            raise err

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

    def reset_hard(self, oid):
        """
        Reset repository to given OID.

        Keyword arguments:
        oid -- Targeted OID.
        """
        assert self.is_open()

        if isinstance(oid, basestring):
            oid = self.repo.lookup_reference(oid).target

        self.repo.reset(oid, pygit2.GIT_RESET_HARD) # pylint: disable=E1101

    @staticmethod
    def handle_git_error(error):
        """
        Translate errors from Gitolite response into well known exceptions.

        Arguments:
        error -- Gitolite error.
        """
        http_matches = re.match(__http_error__, error.message)
        if http_matches and int(http_matches.group(1)) == 401:
            return ForbiddenException()
        elif re.match(__forbidden_pattern__, error.message):
            return ForbiddenException()
        else:
            return error
