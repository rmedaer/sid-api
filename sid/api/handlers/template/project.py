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
                log_message='Not any template installed on this project'
            )

        # Return template from SID object
        name, version = self.project.get_template()
        self.write({
            'name': name,
            'version': version
        })

    @auth.require_authentication()
    @http.accepted_content_type(['application/json'])
    @http.available_content_type(['application/json'])
    @http.parse_json_body(TEMPLATE_SCHEMA)
    def put(self, project_name, *args, **kwargs):
        """
        Install or upgrade specified template on targeted project.

        Example:
        > PUT /projects/example/template HTTP/1.1
        > Accept: */*
        > Content-Type: application/json
        > Content-Length: 76
        >
        {"name":"my-template", "version":"1.0.0", "data":{"customer":"example.com"}}
        """
        template_name = kwargs['json']['name']
        template_version = kwargs['json']['version']
        template_data = kwargs['json']['data']

        # Fetch and load the project and template
        self.prepare_project(project_name)
        self.prepare_template(template_name)

        # Install procedure (if not any template installed previously)
        if not self.project.has_template():
            # Check if version is available
            self._check_template_version(template_version)

            # Validate template schema
            self._check_template_data(template_data)

            # Install template to the project
            self.project.install_template(
                self.template,
                template_version,
                template_data
            )

        # Upgrade procedure if current template name equals given one
        else:
            if self.template.get_name() != template_name:
                raise HTTPError(
                    status_code=409,
                    log_message='A template is already installed on this project'
                )

            # Check if version is available
            self._check_template_version(template_version)

            # Validate template schema
            self._check_template_data(template_data)

            # Upgrade template
            # NOTE Should we check if new version is younger ????
            # If yes, where do we check ? Here or in model (Project class)
            self.project.upgrade_template(
                template_version,
                template_data
            )

    def _check_template_version(self, version):
        """
        Check if version is available for loaded template or raise a 400 error.

        It will also checkout given version on local template copy.

        Arguments:
        version -- Template version.
        """
        if version not in self.template.get_versions():
            raise HTTPError(
                status_code=400,
                log_message='Version \'%s\' could not be found for this template' % version
            )

        self.template.checkout_version(version)

    def _check_template_data(self, data):
        """
        Check if user data are valid for loaded template.

        Arguments:
        data -- Data to validate.
        """
        try:
            self.template.validate(data)
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
