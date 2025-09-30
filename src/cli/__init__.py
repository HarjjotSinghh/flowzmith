"""
Flowzmith CLI Package

This package provides command-line interface functionality for the Flowzmith application.
"""

from .api_client import APIClient
from .contract_creator import ContractCreator
from .deployment_manager import DeploymentManager
from .doc_search import DocumentationSearch
from .suggestions import suggestions

__version__ = "1.0.0"
__all__ = ["APIClient", "ContractCreator", "DeploymentManager", "DocumentationSearch", "suggestions"]