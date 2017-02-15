# -*- coding: utf-8 -*-

""" Default handler

This handler should receive every request not routed to another handler.
It will almost respond with a "404 - Not Found" error.
"""

from tornado.web import HTTPError
from .error import ErrorHandler

class DefaultHandler(ErrorHandler):
    """ Default handler. See module documentation. """

    def prepare(self):
        """ Almost raise a "404 - Not Found" error """
        raise HTTPError(
            status_code=404,
            log_message='Resource not found.'
        )
