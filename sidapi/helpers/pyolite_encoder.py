# -*- coding: utf-8 -*-

from json import JSONEncoder
from pyolite2 import RepositoryCollection, Repository, Rule

from .. import __projects_prefix__

def repository_rule(rule):
    return dict(
        perm=rule.perm,
        users=rule
    )

class PyoliteEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Repository):
            name = obj.name

            if name.startswith(__projects_prefix__):
                name = name[len(__projects_prefix__):]

            return dict(
                name=name,
                rules=map(repository_rule, obj.rules())
            )
        else:
            return JSONEncoder.default(self, obj)
