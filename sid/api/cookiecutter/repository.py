"""
This module contains an abstraction of Cookiecutter repository.
"""

import os
import json
import jsonschema
from tornado.web import HTTPError
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import (
    NonTemplatedInputDirException,
    UndefinedVariableInTemplate,
    UnknownExtension
)
from sid.api.git import (
    GitRepository,
    GitRepositoryNotFound,
    GitRemoteDuplicate,
    GitBranchNotFound
)

VARS_FILE = 'cookiecutter.json'
README_FILE = 'README.md'

class CookiecutterRepository(GitRepository):
    """
    This class represents a Cookiecutter template behind a Git repository.
    """

    def __init__(self, path):
        """
        Initialize our Cookiecutter repository.
        """
        GitRepository.__init__(self, path)

    def validate(self, data):
        schema = self.get_schema()

        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as vlde:
            raise HTTPError(
                status_code=400,
                log_message='JSON error: %s' % vlde.message
            )
        except jsonschema.SchemaError:
            # TODO log SchemaError for administrators and developpers
            raise HTTPError(
                status_code=500,
                log_message='Invalid JSON schema. '
                            'Please contact your administrator.'
            )

    def apply(self, dst_path, data={}):
        """
        Apply this template to given path.
        """
        assert self.is_open()

        try:
            cookiecutter(
                self.path,
                no_input=True,
                extra_context=data,
                replay=False,
                overwrite_if_exists=True,
                output_dir=dst_path,
                strip=True
            )
        except NonTemplatedInputDirException as err:
            raise HTTPError(
                status_code=500,
                log_message='Malformed template directory: %s.' % err.__class__.__name__
            )
        except UndefinedVariableInTemplate as err:
            raise HTTPError(
                status_code=500,
                log_message='An undefined variable was found while installing '
                            'the template. %s' % err.message
            )
        except UnknownExtension as err:
            raise HTTPError(
                status_code=500,
                log_message='An extension was missing while installing '
                            'the template. %s' % err.message
            )

    def get_schema(self):
        """
        Read Cookiecutter schema.
        """
        assert self.is_open()

        # Cookiecutter doesn't have a "real" JSON schema. The Cookiecutter.rc
        # file is just a set of key=question.
        # We are translating that into a standard JSON schema.

        try:
            file = open(os.path.join(self.path, VARS_FILE), 'r')
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Unable to read template file: %s. '
                            'Please contact your system administrator.' % VARS_FILE
            )


        rc = json.loads(file.read())
        if not isinstance(rc, dict):
            raise HTTPError(
                status_code=500,
                log_message='Unrecognized %s format. '
                            'Please contact your system administrator.' % VARS_FILE
            )

        schema = {
            'properties': {},
            'required': [],
            'additionalProperties': True
        }
        for key in rc:
            schema['properties'][key] = {
                "type": "string"
            }
            # Until I don't know how to set default values in schema using
            # 'jsonschema' library, all the properties are mandatory.
            schema['required'].append(key)

        return schema

    def get_readme(self):
        assert self.is_open()

        try:
            file = open(os.path.join(self.path, README_FILE), 'r')
        except IOError:
            raise HTTPError(
                status_code=500,
                log_message='Unable to read template README  (%s). '
                            'Please contact your system administrator.' % README_FILE
            )

        return file.read()
