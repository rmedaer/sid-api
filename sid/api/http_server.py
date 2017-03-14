"""
HTTP server main file.

This file contains the HTTP server initialization script.
It's building all the project routes and connect them to their handlers.
"""

import anyconfig
import tornado
import tornado.process
from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.ioloop import IOLoop
from jsonschema import validate, ValidationError

from sid.api.handlers.misc import (
    NotFoundHandler,
    VersionHandler
)
from sid.api.handlers.project import (
    ProjectCollectionHandler,
    ProjectHandler,
    ProjectDeploymentHandler
)
from sid.api.handlers.template import (
    TemplateCollectionHandler,
    TemplateHandler
)

from sid.api.schemas import CONFIGURATION_SCHEMA

def create_app(settings):
    """ Create a Tornado application. """

    return Application([
        # (r"/projects/(\S+)/settings/(\S+)", SettingsHandler),
        # (r"/projects/(\S+)/settings", SettingsCollectionHandler),
        # (r"/projects/(\S+)/template", ProjectTemplateHandler),
        (r"/projects/(\S+)/deploy", ProjectDeploymentHandler),
        (r"/projects/(\S+)", ProjectHandler),
        (r"/projects", ProjectCollectionHandler),
        (r"/templates/(\S+)", TemplateHandler),
        (r"/templates", TemplateCollectionHandler),
        (r"/version", VersionHandler),
        (r".*", NotFoundHandler)
    ], **settings)

def main(config_file='/etc/sid/api.conf'):
    """
    Instance and start a tornado HTTP server with configuration.
    """

    # Read configuration file
    try:
        config = anyconfig.load(config_file, ac_parser='ini')
        validate(config, CONFIGURATION_SCHEMA)
    except ValidationError as err:
        raise AssertionError('Configuration error: ' + err.message)
    except IOError:
        raise AssertionError('Unable to read configuration file')

    # Read public key file
    try:
        public_key_path = config.get('auth').get('public_key_file')
        with open(public_key_path, 'r') as public_key_file:
            config.get('auth')['public_key'] = public_key_file.read()
    except IOError:
        raise AssertionError('Unable to read public key file: %s' % public_key_path)

    # Create our tornado application
    app = create_app(config)

    # Instance the web server
    sockets = tornado.netutil.bind_sockets(config.get('http', {}).get('port', 80))
    tornado.process.fork_processes(0)
    server = HTTPServer(app)
    server.add_sockets(sockets)
    IOLoop.current().start()

if __name__ == "__main__": # pragma: no cover
    main()
