# -*- coding: utf-8 -*-

""" Pyolite handler.

This handler generate JSON based on Pyolite objects.
"""

from json import JSONEncoder, dumps
from tornado.web import RequestHandler, HTTPError
from pyolite2 import RepositoryCollection, Repository, Rule

def repository_name(repository):
    return repository.name

def repository_rule(rule):
    return dict(
        perm=rule.perm,
        refex=rule.refex,
        users=rule
    )

class SerializerEncoder(JSONEncoder):
    def iterencode(self, obj, _one_shot=False):
        rendered = obj

        if isinstance(obj, RepositoryCollection):
            rendered = map(repository_name, obj)

        return JSONEncoder.iterencode(self, rendered, _one_shot)

    def default(self, obj):
        if isinstance(obj, Repository):
            return dict(
                name=obj.name,
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
