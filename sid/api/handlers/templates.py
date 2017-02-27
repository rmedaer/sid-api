"""
This module contains handler which manage a template collection from Gitolite
configuration.
"""

from pyolite2 import RepositoryNotFoundError
from tornado.web import HTTPError

# Local imports
import sid.api.http as http
import sid.api.auth as auth
from sid.api import __templates_prefix__
from sid.api.handlers.workspace import WorkspaceHandler
from sid.api.schemas import TEMPLATE_SCHEMA

@http.json_error_handling
@http.json_serializer
class TemplateCollectionHandler(WorkspaceHandler):
    """
    This handler process following routes:

        - GET /templates -- List available templates
    """

    def prepare(self, *args, **kwargs):
        """
        Prepare user's workspace and Pyolite configuration to manage templates.
        """
        super(TemplateCollectionHandler, self).prepare()
        self.pyolite = self.prepare_pyolite()

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
                    for project in self.pyolite.repos
                    if project.name.startswith(__templates_prefix__)])

@http.json_error_handling
@http.json_serializer
class TemplateHandler(WorkspaceHandler):
    """
    This handler process following routes:

        - GET /templates/<template_name> -- Get template information from its name
    """

    def prepare(self, *args, **kwargs):
        """
        Prepare user's workspace and Pyolite configuration to manage templates.
        """
        super(TemplateHandler, self).prepare()
        self.pyolite = self.prepare_pyolite()

    @auth.require_authentication()
    @http.available_content_type([
        'text/markdown',
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
            repo = self.pyolite.repos[__templates_prefix__ + template_name]
        except RepositoryNotFoundError:
            raise HTTPError(
                status_code=404,
                log_message='Template not found.'
            )

        # Load template
        template = self.prepare_template(template_name)

        if output_content_type == 'application/json':
            self.write(repo)

        elif output_content_type == 'application/schema+json':
            self.write(template.get_schema())

        elif output_content_type == 'text/markdown':
            self.write(template.get_readme())

@http.json_error_handling
@http.json_serializer
class ProjectTemplateHandler(WorkspaceHandler):
    """
    This handler process following routes:

        - GET /projects/<project_name>/template -- Get information about template installed on given project
        - PUT /projects/<project_name>/template -- Install a template on targeted project
    """

    def prepare(self, *args, **kwargs):
        """
        Prepare user's workspace and Pyolite configuration to manage templates.
        """
        super(ProjectTemplateHandler, self).prepare()

    def get(self, project_name, *args, **kwargs):
        """
        TODO
        """

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
        {"name":"my-template","data":{"customer":"example.com"}}
        """
        template_name = kwargs['json']['name']

        # Fetch and load the targeted project
        project = self.prepare_project(project_name)

        # TODO Test if a template is not already installed on this project

        # Fetch template
        template = self.prepare_template(template_name)

        # Validate template schema
        template.validate(kwargs['json']['data'])

        # Apply it to our repository
        template.apply(project.path, kwargs['json']['data'])

        # Commit all changes made in Git repository
        project.commit_all('Installed template: %s' % template_name)
