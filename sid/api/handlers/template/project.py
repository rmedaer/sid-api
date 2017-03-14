"""
ProjectTemplateHandler module (see handler documentation)
"""

from jsonschema import ValidationError, SchemaError
from tornado.web import HTTPError
from sid.api import http, auth
from sid.api.handlers.project import AbstractProjectHandler
from sid.api.handlers.template import AbstractTemplateHandler
from sid.api.schemas import TEMPLATE_SCHEMA

@http.json_error_handling
@http.json_serializer
class ProjectTemplateHandler(AbstractTemplateHandler, AbstractProjectHandler):
    """
    This handler process following routes:

        - GET /projects/<project_name>/template -- Get information about template installed on given project
        - PUT /projects/<project_name>/template -- Install a template on targeted project
    """

    def get(self, project_name, *args, **kwargs):
        """
        Get installed template on given project
        """
        # Fetch and load the targeted project
        self.prepare_project(project_name)

        if not self.project.has_template():
            raise HTTPError(
                status_code=404,
                log_message='No template installed on this project'
            )

        # TODO format and return
        self.project.get_template()

    @auth.require_authentication()
    @http.accepted_content_type(['application/json'])
    @http.available_content_type(['application/json'])
    @http.parse_json_body(TEMPLATE_SCHEMA)
    def put(self, project_name, *args, **kwargs):
        """
        Install specified template on targeted project.
        TODO: Implement upgrade procedure using the idea from @aroig
        https://github.com/audreyr/cookiecutter/issues/784

        Example:
        > PUT /projects/example/template HTTP/1.1
        > Accept: */*
        > Content-Type: application/json
        > Content-Length: 56
        >
        {"name":"my-template", "data":{"customer":"example.com"}}
        """
        template_name = kwargs['json']['name']

        # Fetch and load the targeted project
        self.prepare_project(project_name)

        if self.project.has_template():
            # TODO test if installed template == given template.
            # If yes => upgrade
            raise HTTPError(
                status_code=409,
                log_message='A template is already installed on this project'
            )

        else:
            # Fetch template
            self.prepare_template(template_name)

            # Validate template schema
            try:
                self.template.validate(kwargs['json']['data'])
            except ValidationError as vlde:
                raise HTTPError(
                    status_code=400,
                    log_message='JSON error: %s' % vlde.message
                )
            except SchemaError:
                raise HTTPError(
                    status_code=500,
                    log_message='Invalid template JSON schema.'
                )

            # Apply it to our repository
            self.project.install_template(self.template, 'TODO', kwargs['json']['data'])
