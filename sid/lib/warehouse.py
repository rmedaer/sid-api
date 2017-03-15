"""
This module contains a class which represent a Gitolite configuration
under a Git repository. Mixing sid.api.git.GitRepository and pyolite2.Pyolite.
"""

import os
import re
from pyolite2 import Pyolite, Rule
from sid.lib.git import Repository

__gitolite_main_file__ = 'conf/gitolite.conf'

class RepositoryPatchException(Exception):
    """
    Exception raised on repository patch failure.
    """
    pass

class Warehouse(Pyolite, Repository):
    """
    A Pyolite configuration under Git repository.
    """

    def __init__(self, path):
        """ Initialize our Pyolite repository. Open its Git repository. """
        Repository.__init__(self, path)
        Pyolite.__init__(self, os.path.join(path, __gitolite_main_file__))

    def load(self):
        # Load Gitolite admin configuration
        Pyolite.load(self)

    def save(self, message, remote='origin'):
        """ Save Gitolite configuration and commit changes. """

        # Save Gitolite configuration
        Pyolite.save(self)

        # Commit all changes made in Git repository
        self.commit_all(message)

        # Push to remote
        self.push(remote)

    @staticmethod
    def patch_pyolite_repo(repo, patches):
        """
        Patch a repository with given JSON patch.

        Keyword arguments:
        repo -- The repository to patch.
        patches -- An array of JSON patches to be applied on given repository.
        """

        for patch in patches:
            # Renaming a project is currently not implemented
            if patch['path'] == '/name' and patch['op'] == 'replace':
                # TODO when implementing, don't forget to validate PROJECT_NAME
                raise RepositoryPatchException('Renaming a project is currently not implemented.')

            # You can only make operations on /rules/{index}
            m_rules = re.match('^/rules/([0-9]*)$', patch['path'])
            if not m_rules:
                raise RepositoryPatchException('Patch not supported.')

            # Add a new rule
            if patch['op'] == 'add':
                # Create a new rule
                rule = Rule(patch['value']['perm'], '')
                rule += patch['value']['users']
                repo.append(rule)

            # Replace an existing rule
            elif patch['op'] == 'replace':
                index = int(m_rules.group(1))
                try:
                    rule = Rule(patch['value']['perm'], '')
                    rule += patch['value']['users']
                    repo.replace_rule(repo.rules()[index], rule)
                except IndexError:
                    raise RepositoryPatchException('Failed to replace rule [%d] (rule not found)' % index)

            # Remove an existing rule
            elif patch['op'] == 'remove':
                index = int(m_rules.group(1))
                try:
                    repo.remove_rule(repo.rules()[index])
                except IndexError:
                    raise RepositoryPatchException('Failed to remove rule [%d] (rule not found)' % index)
