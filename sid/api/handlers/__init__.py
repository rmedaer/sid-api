# -*- coding: utf-8 -*-

""" Handler __init__ script. """

from not_found import NotFoundHandler
from not_implemented import NotImplementedHandler
from projects import ProjectHandler, ProjectCollectionHandler, ProjectDeploymentHandler
from templates import TemplateHandler, TemplateCollectionHandler, ProjectTemplateHandler
from version import VersionHandler
from workspace import WorkspaceHandler
from settings import SettingsCollectionHandler, SettingsHandler
