"""
TemplateHandler module (see handler documentation)
"""

import pyolite2
from tornado.web import HTTPError
from sid.api import http, auth
from sid.api.handlers.template import AbstractTemplateHandler
from sid.api.handlers.warehouse import AbstractWarehouseHandler
from sid.lib.template import TemplateException

__templates_prefix__ = 'templates/'

@http.json_error_handling
@http.json_serializer
class TemplateHandler(AbstractWarehouseHandler, AbstractTemplateHandler):
    """
    This handler process following routes:

        - GET /templates/<template_name> -- Get template information from its name
    """

    @auth.require_authentication()
    @http.available_content_type([
        'application/schema+json',
        'application/json'
    ])
    def get(self, template_name, *args, **kwargs):
        """
        Fetch template and get its details.

        Example:
        > GET /templates/example HTTP/1.1
        > Accept: */*
        >
        """
        output_content_type = kwargs.get('output_content_type')

        # Get repository
        try:
            self.warehouse.repos[__templates_prefix__ + template_name]
        except pyolite2.errors.RepositoryNotFoundException:
            raise HTTPError(
                status_code=404,
                log_message='Template not found.'
            )

        # Load template
        self.prepare_template(template_name)

        # TODO We should checkout in given version (or master if not specified)

        if output_content_type == 'application/json':
            self.write({
                'name': self.template.get_name(),
                'versions': self.template.get_versions()
            })

        elif output_content_type == 'application/schema+json':
            try:
                self.write(self.template.get_schema())
            except TemplateException as error:
                raise HTTPError(
                    status_code=500,
                    log_message=error.message
                )
