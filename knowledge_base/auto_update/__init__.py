"""
Auto-update module for the knowledge base.

Provides file system monitoring and automatic document processing.
"""

from .file_watcher import KnowledgeBaseUpdater, NewFileHandler

__all__ = ["KnowledgeBaseUpdater", "NewFileHandler"]