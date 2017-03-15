"""
This module contains JSON encoder for SID API.
"""

from json import JSONEncoder
from pyolite2 import Repository

__templates_prefix__ = 'templates/'
__projects_prefix__ = 'projects/'

class Encoder(JSONEncoder):
    """
    JSON encoder for Pyolite classes.
    """

    def default(self, obj): # pylint: disable=E0202
        """
        Default encoding method.

        Keyword arguments:
        obj -- Object to serialize.
        """

        # TODO REVIEW Since Repository are specified (Project, Template)
        # We can take their name from object insteadof "startswith technic"
        if isinstance(obj, Repository):
            name = obj.name

            # Remove prefixes of projects and templates
            if name.startswith(__projects_prefix__):
                name = name[len(__projects_prefix__):]
            if name.startswith(__templates_prefix__):
                name = name[len(__templates_prefix__):]

            # Format Repository with only the name and its rules
            return dict(
                name=name,
                rules=[dict(perm=rule.perm, users=rule)
                       for rule in obj.rules()]
            )
        else: # pragma: no cover
            return JSONEncoder.default(self, obj)
