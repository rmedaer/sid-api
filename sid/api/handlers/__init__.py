# -*- coding: utf-8 -*-

""" Handler __init__ script. """

from sid.api.handlers.not_found import NotFoundHandler
from sid.api.handlers.not_implemented import NotImplementedHandler
from sid.api.handlers.projects import ProjectHandler, ProjectCollectionHandler, ProjectDeploymentHandler
from sid.api.handlers.templates import TemplateHandler, TemplateCollectionHandler, ProjectTemplateHandler
from sid.api.handlers.version import VersionHandler
from sid.api.handlers.workspace import WorkspaceHandler
from sid.api.handlers.settings import SettingsCollectionHandler, SettingsHandler
