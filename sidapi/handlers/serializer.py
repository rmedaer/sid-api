# -*- coding: utf-8 -*-

""" This module contains a RequestHandler which serialize known object to JSON """

import json
from tornado.web import RequestHandler
from sidapi.helpers import PyoliteEncoder

class SerializerHandler(RequestHandler):
    """ This RequestHandler override `write` method to serialize known object into JSON """

    def write(self, chunk):
        """ Encode known objects to body """
        # TODO What happening on encoding failure ? Do we have to handle that
        # with a HTTPError 500 ?
        return RequestHandler.write(
            self,
            json.dumps(chunk, cls=PyoliteEncoder, sort_keys=True)
        )

    def data_received(self, chunk): # pragma: no cover
        """ Not implemented ! """
        return
