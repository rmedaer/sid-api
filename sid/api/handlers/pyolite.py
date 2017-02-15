# -*- coding: utf-8 -*-

""" This module contains a generic handler which manage initialize and prepare
a Pyolite configuration. """

from tornado.web import HTTPError
from pyolite2 import FileError
from sid.api.handlers.error import ErrorHandler
from sid.lib import PyoliteRepository, GitRepositoryNotFound

class PyoliteHandler(ErrorHandler):
    """ Abstract handler for Pyolite configuration. """

    def initialize(self, admin_config):
        """ Initialize pyolite handler. Storing admin_config path. """

        self.pyolite = None
        self.admin_config = admin_config

    def prepare(self):
        """ Prepare handler by instanciating and loading Pyolite configuration. """

        try:
            self.pyolite = PyoliteRepository(self.admin_config)
            self.pyolite.load()
        except (FileError, GitRepositoryNotFound):
            raise HTTPError(
                status_code=503,
                log_message='Projects management temporary unavailable.'
            )
