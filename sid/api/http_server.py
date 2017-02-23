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
    NotFoundHandler,
    NotImplementedHandler,
    ProjectHandler,
    ProjectCollectionHandler,
    ProjectTemplateHandler,
    ProjectDeploymentHandler,
    SettingsHandler,
    SettingsCollectionHandler,
    TemplateCollectionHandler,
    TemplateHandler,
    VersionHandler,
    WorkspaceHandler
)

def create_app(settings):
    """ Create a Tornado application. """

    return Application([
        (r"/projects/(\S+)/settings/(\S+)", SettingsHandler),
        (r"/projects/(\S+)/settings", SettingsCollectionHandler),
        (r"/projects/(\S+)/template", ProjectTemplateHandler),
        (r"/projects/(\S+)/deploy", ProjectDeploymentHandler),
        (r"/projects/(\S+)", ProjectHandler),
        (r"/projects", ProjectCollectionHandler),
        (r"/templates/(\S+)", TemplateHandler),
        (r"/templates", TemplateCollectionHandler),
        (r"/version", VersionHandler),
        (r".*", NotFoundHandler)
    ], **settings)

def main(port=80): # pragma: no cover
    """ Instance and start a tornado HTTP server. """

    settings = dict(
        workspace_dir='/var/lib/sid/workspaces',
        remote_url='http://git.warehouse.sid.com/'
    )

    app = create_app(settings)

    sockets = tornado.netutil.bind_sockets(port)
    tornado.process.fork_processes(0)
    server = HTTPServer(app)
    server.add_sockets(sockets)
    IOLoop.current().start()

if __name__ == "__main__": # pragma: no cover
    main()
