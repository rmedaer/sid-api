"""
This package contains every handlers linked to "project" resource management
such as:
  - ProjectCollectionHandler which manage a collection of projects
  - ProjectHandler which manage project itself
"""

from .abstract_project import AbstractProjectHandler
from .collection import ProjectCollectionHandler
from .project import ProjectHandler
from .deploy import ProjectDeploymentHandler
