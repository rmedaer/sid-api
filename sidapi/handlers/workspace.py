
# Global imports
from json import loads
from jsonschema import validate, ValidationError
from tornado.web import HTTPError
from pyolite2 import RepositoryDuplicateError, Repository

# Local imports
from .error import ErrorHandler
from .serializer import SerializerHandler
from ..objects import PyoliteRepository
from ..decorators import negociate_content_type, accepted_content_type

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

    def prepare(self):
        self.pyolite = PyoliteRepository(self.admin_config)

        try:
            self.pyolite.load()
        except:
            raise HTTPError(
                status_code=503,
                log_message='Projects management temporary unavailable.'
            )

    @negociate_content_type(['application/json'])
    def get(self):
        """ List available projects within this workspace. """
        self.write(self.pyolite.repos)

    @negociate_content_type(['application/json'])
    @accepted_content_type(['application/json'])
    def post(self):
        try:
            # Parse JSON
            data = loads(self.request.body)
        except ValueError:
            raise HTTPError(
                status_code=400,
                log_message='Unable to parse JSON body.'
            )

        try:
            # Validate JSON schema
            validate(data, POST_PROJECT)

            # Create and add repository
            repo = Repository(data['name'])
            self.pyolite.repos.append(repo)

            # TODO add default user permission
        except ValidationError as ve:
            raise HTTPError(
                status_code=400,
                log_message='JSON error: %s' % ve.message
            )
        except RepositoryDuplicateError:
            raise HTTPError(
                status_code=409,
                log_message='Repository \'%s\' already exists' % data['name']
            )

        try:
            # Save Gitolite configuration and commit changes
            self.pyolite.save('Created project \'%s\'' % data['name'])
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Failed to save changes'
            )

        # Return created repository
        self.write(repo)
