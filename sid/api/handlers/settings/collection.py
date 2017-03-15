"""
SettingsCollectionHandler module (see handler documentation)
"""

import os
from whiriho import Whiriho
from whiriho.errors import CatalogNotFoundException, WhirihoException
from tornado.web import HTTPError
from sid.api import http, auth
from sid.api.handlers.project import AbstractProjectHandler

__whiriho_catalog__ = 'whiriho.json'

@http.json_error_handling
@http.json_serializer
class SettingsCollectionHandler(AbstractProjectHandler):
    """
    This handler process following routes:

        - GET /projects/<project_name>/settings -- List available settings in given project
    """

    @auth.require_authentication()
    @http.available_content_type(['application/json'])
    def get(self, project_name, *args, **kwargs):
        """
        Get list of available settings.

        Example:
        > GET /projects/example/settings HTTP/1.1
        > Accept: */*
        >
        """

        self.prepare_project(project_name)

        try:
            whiriho = Whiriho(os.path.join(self.project.path, __whiriho_catalog__))
            whiriho.load()
            self.write(whiriho.get_paths())
        except CatalogNotFoundException:
            self.write([])
        except WhirihoException as error:
            raise HTTPError(
                status_code=500,
                log_message='Catalog error (%s)' % error.message
            )
