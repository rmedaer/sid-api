# -*- coding: utf-8 -*-

import json
from tornado.web import RequestHandler, HTTPError
from ..helpers import PyoliteEncoder

class SerializerHandler(RequestHandler):

    def write(self, chunk, callback=None):
        return RequestHandler.write(self, json.dumps(chunk, cls=PyoliteEncoder, sort_keys=True))

    def data_received(self, chunk):
        """ Not implemented ! """
        return
