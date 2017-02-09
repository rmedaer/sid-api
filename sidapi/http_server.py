# -*- coding: utf-8 -*-

"""HTTP server main file.

This file contains the HTTP server initialization script.
It's building all the project routes and connect them to their handlers.
"""

from tornado.web import Application
from tornado.ioloop import IOLoop
from .handlers import (
    VersionHandler,
    DefaultHandler,
    NotImplementedHandler,
    WorkspaceHandler,
    ProjectHandler,
    TemplateHandler,
    TemplateCollectionHandler
)

def main(port=80):
    """ Instance and start a tornado HTTP server. """

    admin_config = "/home/rme/Documents/Development/sid/gitolite-admin-test/gitolite.conf"

    app = Application([
        (r"/projects", WorkspaceHandler, dict(admin_config=admin_config)),
        (r"/projects/(.*)", ProjectHandler, dict(admin_config=admin_config)),
        (r"/projects/(.*)/push", NotImplementedHandler),
        (r"/projects/(.*)/settings", NotImplementedHandler),
        (r"/projects/(.*)/settings/(.*)", NotImplementedHandler),
        (r"/projects/(.*)/template", NotImplementedHandler),
        (r"/templates", TemplateCollectionHandler, dict(admin_config=admin_config)),
        (r"/templates/(.*)", TemplateHandler, dict(admin_config=admin_config)),
        (r"/version", VersionHandler),
        (r".*", DefaultHandler)
    ])
    app.listen(port)
    IOLoop.current().start()

if __name__ == "__main__":
    main()
