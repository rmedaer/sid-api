# -*- coding: utf-8 -*-

"""HTTP server main file.

This file contains the HTTP server initialization script.
It's building all the project routes and connect them to their handlers.
"""

from tornado.web import Application
from tornado.ioloop import IOLoop
from .handlers import VersionHandler, DefaultHandler

def main(port=80):
    """ Instance and start a tornado HTTP server. """
    app = Application([
        (r"/version", VersionHandler),
        (r".*", DefaultHandler)
    ])
    app.listen(port)
    IOLoop.current().start()

if __name__ == "__main__":
    main()
