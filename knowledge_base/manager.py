"""
Main Knowledge Base Manager class.

Provides a unified interface for all knowledge base operations including
document ingestion, search, and auto-updating functionality.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from .ingestion import DocumentProcessor
from .storage import VectorStoreManager
from .search import KnowledgeQueryEngine
from .auto_update import KnowledgeBaseUpdater

logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """Main manager class for the knowledge base system."""

    def __init__(
        self,
        knowledge_base_path: str = "./knowledge_base",
        collection_name: str = "smart_contracts",
        embedding_model: str = "text-embedding-ada-002",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        watch_directories: Optional[List[str]] = None,
        auto_update_enabled: bool = True,
        debounce_seconds: int = 10
    ):
        """
        Initialize the knowledge base manager.

        Args:
            knowledge_base_path: Base path for knowledge base storage
            collection_name: Name for the ChromaDB collection
            embedding_model: OpenAI embedding model to use
            chunk_size: Size of document chunks
            chunk_overlap: Overlap between chunks
            watch_directories: Directories to monitor for auto-updates
            auto_update_enabled: Whether to enable auto-updating
            debounce_seconds: Debounce time for file system events
        """
        self.knowledge_base_path = Path(knowledge_base_path)
        self.collection_name = collection_name
        self.auto_update_enabled = auto_update_enabled

        # Create paths
        self.storage_path = self.knowledge_base_path / "storage"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.document_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        self.vector_store_manager = VectorStoreManager(
            collection_name=collection_name,
            persist_directory=str(self.storage_path),
            embedding_model=embedding_model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        self.query_engine = KnowledgeQueryEngine(
            vector_store_manager=self.vector_store_manager,
            document_processor=self.document_processor
        )

        # Initialize auto-updater if enabled
        self.knowledge_base_updater = None
        if auto_update_enabled and watch_directories:
            self.knowledge_base_updater = KnowledgeBaseUpdater(
                watch_directories=watch_directories,
                vector_store_manager=self.vector_store_manager,
                document_processor=self.document_processor,
                collection_name=f"{collection_name}_auto_update",
                debounce_seconds=debounce_seconds
            )

        # Statistics and metadata
        self.init_stats = {
            "initialized_at": datetime.now().isoformat(),
            "auto_update_enabled": auto_update_enabled,
            "watch_directories": watch_directories or [],
            "components": {
                "document_processor": True,
                "vector_store_manager": True,
                "query_engine": True,
                "auto_updater": self.knowledge_base_updater is not None
            }
        }

        logger.info(f"Knowledge Base Manager initialized with collection: {collection_name}")

    def add_documents(
        self,
        source: Union[str, Path, List[Union[str, Path]]],
        source_type: str = "file",
        metadata: Optional[Dict[str, Any]] = None,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Add documents to the knowledge base.

        Args:
            source: Path(s) to files/directories to process
            source_type: Type of source ("file", "directory", "text")
            metadata: Additional metadata to add to documents
            batch_size: Batch size for processing
        """
        try:
            logger.info(f"Adding documents from {source_type}: {source}")

            if source_type == "file":
                if isinstance(source, (str, Path)):
                    documents = self.document_processor.process_file(source)
                else:
                    documents = []
                    for file_path in source:
                        documents.extend(self.document_processor.process_file(file_path))

            elif source_type == "directory":
                documents = self.document_processor.process_directory(source)

            elif source_type == "text":
                if isinstance(source, str):
                    documents = self.document_processor.process_text(source, metadata)
                else:
                    raise ValueError("Text source must be a string")

            else:
                raise ValueError(f"Unsupported source type: {source_type}")

            if not documents:
                return {
                    "success": False,
                    "error": "No documents extracted from source",
                    "source": str(source),
                    "source_type": source_type
                }

            # Add metadata if provided
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)

            # Add to vector store
            result = self.vector_store_manager.add_documents(documents, batch_size)

            return {
                "success": result["success"],
                "documents_added": len(documents),
                "source": str(source),
                "source_type": source_type,
                "stats": result.get("stats", {}),
                "error": result.get("error")
            }

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": str(source),
                "source_type": source_type
            }

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        similarity_threshold: float = 0.7,
        search_type: str = "semantic",
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Search the knowledge base.

        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Metadata filters to apply
            similarity_threshold: Minimum similarity score
            search_type: Type of search ("semantic", "keyword", "hybrid")
            include_metadata: Whether to include document metadata
        """
        return self.query_engine.search(
            query=query,
            top_k=top_k,
            filters=filters,
            similarity_threshold=similarity_threshold,
            include_metadata=include_metadata,
            search_type=search_type
        )

    def start_auto_update(self) -> Dict[str, Any]:
        """Start the auto-updating file watcher."""
        if not self.knowledge_base_updater:
            return {
                "success": False,
                "error": "Auto-updater not initialized"
            }

        try:
            self.knowledge_base_updater.start_watching()
            return {
                "success": True,
                "message": "Auto-update started successfully",
                "watch_directories": self.knowledge_base_updater.watch_directories
            }
        except Exception as e:
            logger.error(f"Failed to start auto-update: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def stop_auto_update(self) -> Dict[str, Any]:
        """Stop the auto-updating file watcher."""
        if not self.knowledge_base_updater:
            return {
                "success": False,
                "error": "Auto-updater not initialized"
            }

        try:
            self.knowledge_base_updater.stop_watching()
            return {
                "success": True,
                "message": "Auto-update stopped successfully"
            }
        except Exception as e:
            logger.error(f"Failed to stop auto-update: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the knowledge base."""
        stats = {
            "init_stats": self.init_stats,
            "vector_store_stats": self.vector_store_manager.get_collection_stats(),
            "search_stats": self.query_engine.get_search_stats(),
            "auto_update_stats": None
        }

        if self.knowledge_base_updater:
            stats["auto_update_stats"] = self.knowledge_base_updater.get_processing_stats()

        return stats

    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all components."""
        health_status = {
            "overall_healthy": True,
            "components": {},
            "issues": []
        }

        try:
            # Check document processor
            health_status["components"]["document_processor"] = {
                "healthy": True,
                "stats": self.document_processor.get_processing_stats()
            }

            # Check vector store
            vector_store_health = self.vector_store_manager.health_check()
            health_status["components"]["vector_store_manager"] = vector_store_health

            # Check query engine
            query_engine_health = self.query_engine.health_check()
            health_status["components"]["query_engine"] = query_engine_health

            # Check auto-updater
            if self.knowledge_base_updater:
                auto_update_health = self.knowledge_base_updater.health_check()
                health_status["components"]["auto_updater"] = auto_update_health

            # Determine overall health
            unhealthy_components = []
            for component, status in health_status["components"].items():
                if isinstance(status, dict) and not status.get("healthy", True):
                    unhealthy_components.append(component)

            if unhealthy_components:
                health_status["overall_healthy"] = False
                health_status["issues"] = [f"Unhealthy component: {comp}" for comp in unhealthy_components]

        except Exception as e:
            health_status["overall_healthy"] = False
            health_status["issues"].append(f"Health check error: {str(e)}")

        return health_status

    def export_knowledge_base(self, export_path: str) -> Dict[str, Any]:
        """Export the knowledge base to a file."""
        try:
            success = self.vector_store_manager.export_data(export_path)
            if success:
                return {
                    "success": True,
                    "message": f"Knowledge base exported to {export_path}",
                    "export_path": export_path
                }
            else:
                return {
                    "success": False,
                    "error": "Export failed"
                }
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def import_knowledge_base(self, import_path: str) -> Dict[str, Any]:
        """Import knowledge base from a file."""
        try:
            success = self.vector_store_manager.import_data(import_path)
            if success:
                return {
                    "success": True,
                    "message": f"Knowledge base imported from {import_path}",
                    "import_path": import_path
                }
            else:
                return {
                    "success": False,
                    "error": "Import failed"
                }
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def cleanup_old_documents(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old documents from the knowledge base."""
        if not self.knowledge_base_updater:
            return {
                "success": False,
                "error": "Auto-updater not initialized - cleanup requires auto-update functionality"
            }

        try:
            result = self.knowledge_base_updater.cleanup_old_documents(days_old)
            return result
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def suggest_related_queries(self, query: str, max_suggestions: int = 5) -> List[str]:
        """Get related query suggestions."""
        return self.query_engine.suggest_related_queries(query, max_suggestions)

    def reset_knowledge_base(self) -> Dict[str, Any]:
        """Reset the knowledge base (delete all data)."""
        try:
            # Stop auto-update if running
            if self.knowledge_base_updater:
                self.stop_auto_update()

            # Reset vector store
            success = self.vector_store_manager.reset_collection()

            if success:
                return {
                    "success": True,
                    "message": "Knowledge base reset successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to reset vector store"
                }
        except Exception as e:
            logger.error(f"Reset failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about available collections."""
        try:
            collections = self.vector_store_manager.list_collections()
            return {
                "success": True,
                "collections": collections,
                "current_collection": self.collection_name
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {
                "success": False,
                "error": str(e)
            }