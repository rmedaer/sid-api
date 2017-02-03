# -*- coding: utf-8 -*-

""" Pyolite handler.

This handler generate JSON based on Pyolite objects.
"""

import json
from json import JSONEncoder
from tornado.web import RequestHandler, HTTPError
from pyolite2 import Pyolite, RepositoryCollection, Repository, Rule
from .error import JsonErrorHandler

def repository_name(repository):
    return repository.name

def repository_rule(rule):
    return dict(
        perm=rule.perm,
        refex=rule.refex,
        users=rule
    )

class PyoliteEncoder(JSONEncoder):
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


class PyoliteHandler(JsonErrorHandler):
    def initialize(self, admin_config):
        self.pyolite = Pyolite(admin_config)

    def prepare(self):
        try:
            self.pyolite.load()
        except:
            raise HTTPError(
                status_code=503,
                log_message='Projects management temporary unavailable.'
            )

    def write(self, chunk, callback=None):
        return RequestHandler.write(self, json.dumps(chunk, cls=PyoliteEncoder))

    def data_received(self, chunk):
        """ Not implemented ! """
        return
