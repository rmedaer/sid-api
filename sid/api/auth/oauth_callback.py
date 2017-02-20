# -*- coding: utf-8 -*-

"""
This module contains an authentication callback for pygit2 library.
"""

from pygit2 import RemoteCallbacks, UserPass

class OAuthCallback(RemoteCallbacks):
    """ OAuth callback class. """

    def __init__(self, username, password):
        """ Class constructor."""

        super(OAuthCallback, self).__init__()

        self.username = username
        self.password = password

    def credentials(self, url, username_from_url, allowed_types): # pylint: disable=E0202
        """ Return credentials. """
        return UserPass(self.username, self.password)
