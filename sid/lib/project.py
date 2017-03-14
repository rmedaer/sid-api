"""
This module contains SID Template object.
"""

from sid.lib.git import Repository

class Project(Repository):
    """
    This class represents a SID project. It's basically a Git repository with
    additional methods.
    """

    def __init__(self, path):
        """
        Construct a template repository.
        """
        super(Project, self).__init__(path)

    def install_template(self, template, version, data):
        """
        Install given template to this project.

        Bridge to Milhoja with version formatting/selection.
        """
        # TODO
        pass

    def upgrade_template(self, version, data):
        """
        Upgrade (previously installed) template.

        Bridge to Milhoja with version formatting/selection.
        """
        # TODO
        pass

    def has_template(self):
        """
        Return True if a template is installed otherwise False.
        """
        # TODO
        pass

    def get_template(self):
        """
        Return installed template.
        """
        # TODO
        pass
