"""
ProjectDeploymentHandler module (see handler documentation)
"""

from tornado.web import HTTPError
from sid.api import http, auth
from sid.api.handlers.project import AbstractProjectHandler
from sid.lib.git import GitAutomaticMergeNotAvailable, ForbiddenException

@http.json_error_handling
@http.json_serializer
class ProjectDeploymentHandler(AbstractProjectHandler):
    """
    This handler process following routes:

        - PUT    /projects/<project_name>/deploy -- Deploy a project
    """

    @auth.require_authentication()
    def put(self, project_name, *args, **kwargs):
        """
        Deploy local changes.

        Example:
        > PUT /projects/example/deploy HTTP/1.1
        > Accept: */*
        >
        """
        # Fetch and load the targeted project
        self.prepare_project(project_name)

        # Calculate diff between local copy and remote
        ahead, behind = self.project.ahead_behind('origin')

        # If there is remote changes, try to apply them locally before pushing
        if behind:
            try:
                self.project.pull('origin')
            except GitAutomaticMergeNotAvailable:
                raise HTTPError(
                    status_code=412,
                    log_message='Your local copy is %d commits behind remote repository. '
                                'If you cannot resolve the issue your self, '
                                'please contact your system administrator.' % behind
                )

        # If we don't have anything to push return OK
        if not ahead:
            self.set_status(200)
            return

        # Push our changes
        try:
            self.project.push('origin')
        except ForbiddenException:
            raise HTTPError(
                status_code=403,
                log_message='You are not authorized to deploy this project'
            )

        # Obviously we cannot return a confirmation that changes has been applied.
        # So we are returning a '202 - Accepted' code.
        self.set_status(202)
