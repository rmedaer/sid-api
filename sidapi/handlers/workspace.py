
# Global imports
from tornado.web import HTTPError
from pyolite2 import RepositoryDuplicateError, Repository

# Local imports
from .. import __projects_prefix__
from .error import ErrorHandler
from .serializer import SerializerHandler
from ..objects import PyoliteRepository
from ..decorators import negociate_content_type, accepted_content_type, parse_json_body

POST_PROJECT = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        }
    },
    "required": [
        "name"
    ],
    "additionalProperties": False
}

class WorkspaceHandler(ErrorHandler, SerializerHandler):
    """ This handler manage a workspace. """

    def initialize(self, admin_config):
        self.pyolite = None
        self.admin_config = admin_config

    @negociate_content_type(['application/json'])
    def prepare(self):
        self.pyolite = PyoliteRepository(self.admin_config)

        try:
            self.pyolite.load()
        except:
            raise HTTPError(
                status_code=503,
                log_message='Projects management temporary unavailable.'
            )

    def get(self):
        """ List available projects within this workspace. """
        def projects_filter(project):
            return project.name.startswith(__projects_prefix__)

        self.write(filter(projects_filter, self.pyolite.repos))

    @accepted_content_type(['application/json'])
    @parse_json_body(POST_PROJECT)
    def post(self):
        try:
            # Create and add repository
            repo = Repository(__projects_prefix__ + self.json['name'])
            self.pyolite.repos.append(repo)

            # TODO add default user permissions
        except RepositoryDuplicateError:
            raise HTTPError(
                status_code=409,
                log_message='Repository \'%s\' already exists' % self.json['name']
            )

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Created project \'%s\'' % self.json['name'])
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return created repository
        self.write(repo)