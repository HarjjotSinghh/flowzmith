"""
Flowzmith Knowledge Base

A comprehensive knowledge management system for smart contract development
with auto-updating capabilities and semantic search.
"""

__version__ = "1.0.0"
__author__ = "Flowzmith Team"

from .ingestion.document_processor import DocumentProcessor
from .storage.vector_store import VectorStoreManager
from .search.query_engine import KnowledgeQueryEngine
from .auto_update.file_watcher import KnowledgeBaseUpdater, NewFileHandler
from .manager import KnowledgeBaseManager

__all__ = [
    "DocumentProcessor",
    "VectorStoreManager",
    "KnowledgeQueryEngine",
    "KnowledgeBaseUpdater",
    "NewFileHandler",
    "KnowledgeBaseManager"
]