# -*- coding: utf-8 -*-

"""HTTP server main file.

This file contains the HTTP server initialization script.
It's building all the project routes and connect them to their handlers.
"""

from pyolite2 import Pyolite
from tornado.web import Application
from tornado.ioloop import IOLoop
from .handlers import (
    VersionHandler,
    DefaultHandler,
    NotImplementedHandler,
    WorkspaceHandler,
    ProjectHandler
)

def main(port=80):
    """ Instance and start a tornado HTTP server. """

    pyolite = Pyolite("/home/rme/Documents/Development/sid/pyolite2/tests/fixtures/gitolite.conf")
    pyolite.load()

    app = Application([
        (r"/projects", WorkspaceHandler, dict(pyolite=pyolite)),
        (r"/projects/(.*)", ProjectHandler, dict(pyolite=pyolite)),
        (r"/projects/(.*)/push", NotImplementedHandler),
        (r"/projects/(.*)/settings", NotImplementedHandler),
        (r"/projects/(.*)/settings/(.*)", NotImplementedHandler),
        (r"/projects/(.*)/template", NotImplementedHandler),
        (r"/templates", NotImplementedHandler),
        (r"/templates/(.*)", NotImplementedHandler),
        (r"/version", VersionHandler),
        (r".*", DefaultHandler)
    ])
    app.listen(port)
    IOLoop.current().start()

if __name__ == "__main__":
    main()
