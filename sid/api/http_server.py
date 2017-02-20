"""
HTTP server main file.

This file contains the HTTP server initialization script.
It's building all the project routes and connect them to their handlers.
"""

import tornado
import tornado.process
from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.ioloop import IOLoop
from .handlers import (
    VersionHandler,
    DefaultHandler,
    NotImplementedHandler,
    ProjectHandler,
    ProjectCollectionHandler,
    TemplateHandler,
    TemplateCollectionHandler,
    ProjectTemplateHandler
)

def create_app(settings):
    """ Create a Tornado application. """

    return Application([
        (r"/projects/(.*)/settings/(.*)", NotImplementedHandler),
        (r"/projects/(.*)/settings", NotImplementedHandler),
        (r"/projects/(.*)/template", ProjectTemplateHandler, settings),
        (r"/projects/(.*)/push", NotImplementedHandler),
        (r"/projects/(.*)", ProjectHandler, settings),
        (r"/projects", ProjectCollectionHandler, settings),
        (r"/templates/(.*)", TemplateHandler, settings),
        (r"/templates", TemplateCollectionHandler, settings),
        (r"/version", VersionHandler),
        (r".*", DefaultHandler)
    ])

def main(port=80): # pragma: no cover
    """ Instance and start a tornado HTTP server. """

    settings = dict(
        workspaces_dir='/var/lib/sid/workspaces',
        remotes_url='http://git.warehouse.sid.com/'
    )

    app = create_app(settings)

    sockets = tornado.netutil.bind_sockets(port)
    tornado.process.fork_processes(0)
    server = HTTPServer(app)
    server.add_sockets(sockets)
    IOLoop.current().start()

if __name__ == "__main__": # pragma: no cover
    main()
