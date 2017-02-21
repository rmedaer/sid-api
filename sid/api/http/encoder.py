from json import JSONEncoder
from pyolite2 import Repository
from sid.api import __projects_prefix__, __templates_prefix__

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
