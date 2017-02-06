# -*- coding: utf-8 -*-

from json import JSONEncoder, dumps
from tornado.web import RequestHandler, HTTPError
from pyolite2 import RepositoryCollection, Repository, Rule

from .. import __projects_prefix__

def repository_name(repository):
    return repository.name

def repository_rule(rule):
    return dict(
        perm=rule.perm,
        refex=rule.refex,
        users=rule
    )

class SerializerEncoder(JSONEncoder):
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


class SerializerHandler(RequestHandler):

    def write(self, chunk, callback=None):
        return RequestHandler.write(self, dumps(chunk, cls=SerializerEncoder))

    def data_received(self, chunk):
        """ Not implemented ! """
        return
