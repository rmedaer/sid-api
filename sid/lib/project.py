"""
This module contains SID Template object.
"""

import os
from urlparse import urlparse
from milhoja import Milhoja
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
        self.template = None

    def initialize(self):
        """
        Override project initialization to load Milhoja template.
        """
        super(Project, self).initialize()

        self.template = Milhoja(self.repo)

    def open(self):
        """
        Override project open to load Milhoja template.
        """
        super(Project, self).open()

        self.template = Milhoja(self.repo)

    def install_template(self, template, version, data):
        """
        Install given template to this project.

        Bridge to Milhoja with version formatting/selection.
        """
        self.assert_is_open()

        if self.is_empty:
            self.commit('Initializing project.')

        self.template.install(
            template.path,
            checkout=version,
            no_input=True,
            extra_context=data
        )

    def upgrade_template(self, version, data):
        """
        Upgrade (previously installed) template.

        Bridge to Milhoja with version formatting/selection.
        """
        self.assert_is_open()

        return self.template.upgrade(
            checkout=version,
            no_input=True,
            extra_context=data
        )

    def has_template(self):
        """
        Return True if a template is installed otherwise False.
        """
        self.assert_is_open()

        return self.template.is_installed()

    def get_template(self):
        """
        Return installed template.

        Raises:
        TemplateNotInstalledException if not any template found.
        """
        assert self.has_template(), 'Not any template installed'

        # Fetch template information from Milhoja
        source, checkout = self.template.get_template()

        # Analyze template source; get parsed url result
        url = urlparse(source)

        # Compute file name from url path
        name = os.path.splitext(os.path.basename(url.path))[0]

        return name, checkout
