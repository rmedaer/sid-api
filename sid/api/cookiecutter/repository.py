"""
This module contains an abstraction of Cookiecutter repository.
"""

import os
import json
from sid.api.git import (
    GitRepository,
    GitRepositoryNotFound,
    GitRemoteDuplicate,
    GitBranchNotFound
)

REMOTE_NAME = 'origin'
VARS_FILE = 'cookiecutter.json'
README_FILE = 'README.md'

class CookiecutterRepository(GitRepository):
    """
    This class represents a Cookiecutter template behind a Git repository.
    """

    def __init__(self, path, origin):
        """
        Initialize our Cookiecutter repository.
        """

        GitRepository.__init__(self, path)
        self.origin = origin


    def load(self):
        # Try to open Git repository
        try:
            self.open()
        except GitRepositoryNotFound:
            self.initialize()

        # Check if remote exists or create it
        try:
            GitRepository.create_remote(self, self.origin, REMOTE_NAME)
        except GitRemoteDuplicate:
            pass

        # Update our local copy
        try:
            self.pull(REMOTE_NAME)
        except GitBranchNotFound:
            raise AssertionError('Remote or local branch not found.')

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
            # TODO Should be replaced by 503 Service Unavailable
            raise AssertionError('Unable to read template vars file: %s' % VARS_FILE)

        rc = json.loads(file.read())
        if not isinstance(rc, dict):
            raise AssertionError('Unrecognized %s format' % VARS_FILE)

        schema = {
            'properties': {},
            'required': [],
            'additionalProperties': False
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
            # TODO Should be replaced by 503 Service Unavailable
            raise AssertionError('Unable to read template README: %s' % README_FILE)

        return file.read()
