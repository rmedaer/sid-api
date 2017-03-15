"""
TemplateCollectionHandler module (see handler documentation)
"""

from sid.api import http, auth
from sid.api.handlers.warehouse import AbstractWarehouseHandler

__templates_prefix__ = 'templates/'

@http.json_error_handling
@http.json_serializer
class TemplateCollectionHandler(AbstractWarehouseHandler):
    """
    This handler process following routes:

        - GET /templates -- List available templates
    """

    @auth.require_authentication()
    @http.available_content_type(['application/json'])
    def get(self, *args, **kwargs):
        """
        List available templates.

        Example:
        > GET /templates HTTP/1.1
        > Accept: */*
        >
        """
        self.write([project
                    for project in self.warehouse.repos
                    if project.name.startswith(__templates_prefix__)])
