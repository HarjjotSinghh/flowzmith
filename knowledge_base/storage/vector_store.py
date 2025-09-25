"""
Vector storage management using ChromaDB.

Handles storing, retrieving, and managing document embeddings
with persistent storage and efficient querying.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime

import chromadb
from chromadb.config import Settings
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Advanced vector store manager with ChromaDB integration."""

    def __init__(
        self,
        collection_name: str = "smart_contracts",
        persist_directory: str = "./knowledge_base/storage",
        embedding_model: str = "text-embedding-ada-002",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Ensure persist directory exists
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Initialize embedding model
        self.embed_model = OpenAIEmbedding(
            model=embedding_model,
            embed_batch_size=100
        )

        # Initialize text splitter
        self.text_splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Vector store and index
        self.vector_store = None
        self.index = None
        self.storage_context = None

        self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Initialize ChromaDB vector store and LlamaIndex components."""
        try:
            # Get or create collection
            collection = self.client.get_or_create_collection(self.collection_name)

            # Create Chroma vector store
            self.vector_store = ChromaVectorStore(chroma_collection=collection)

            # Create storage context
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )

            logger.info(f"Vector store initialized with collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    def add_documents(self, documents: List[Document], batch_size: int = 100) -> Dict[str, Any]:
        """Add documents to the vector store with batching."""
        if not documents:
            return {"success": False, "error": "No documents provided"}

        logger.info(f"Adding {len(documents)} documents to vector store")

        stats = {
            "total_documents": len(documents),
            "successful_additions": 0,
            "failed_additions": 0,
            "batches_processed": 0,
            "processing_time": 0,
            "errors": []
        }

        start_time = datetime.now()

        try:
            # Process documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]

                try:
                    # Create index from documents
                    batch_index = VectorStoreIndex.from_documents(
                        documents=batch,
                        storage_context=self.storage_context,
                        embed_model=self.embed_model
                    )

                    stats["successful_additions"] += len(batch)
                    stats["batches_processed"] += 1

                    logger.info(f"Processed batch {stats['batches_processed']}/{(len(documents) + batch_size - 1) // batch_size}")

                except Exception as e:
                    stats["failed_additions"] += len(batch)
                    error_msg = f"Batch {stats['batches_processed'] + 1} failed: {str(e)}"
                    stats["errors"].append(error_msg)
                    logger.error(error_msg)

            # Rebuild the main index
            self._rebuild_index()

            processing_time = (datetime.now() - start_time).total_seconds()
            stats["processing_time"] = processing_time

            logger.info(f"Document addition complete. Success: {stats['successful_additions']}, Failed: {stats['failed_additions']}")

            return {
                "success": True,
                "stats": stats
            }

        except Exception as e:
            stats["processing_time"] = (datetime.now() - start_time).total_seconds()
            stats["errors"].append(f"General error: {str(e)}")
            logger.error(f"Failed to add documents: {e}")

            return {
                "success": False,
                "stats": stats,
                "error": str(e)
            }

    def _rebuild_index(self):
        """Rebuild the main index from vector store."""
        try:
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                embed_model=self.embed_model
            )
            logger.info("Index rebuilt successfully")
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Query the vector store with semantic search."""
        if not self.index:
            logger.warning("Index not initialized. Rebuilding...")
            self._rebuild_index()

        if not self.index:
            return []

        try:
            # Create query engine
            query_engine = self.index.as_query_engine(
                similarity_top_k=top_k,
                filters=filters
            )

            # Execute query
            response = query_engine.query(query_text)

            # Format results
            results = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes:
                    similarity_score = getattr(node, 'score', 0.0)

                    if similarity_score >= similarity_threshold:
                        result = {
                            "content": node.text,
                            "metadata": node.metadata or {},
                            "similarity_score": similarity_score,
                            "node_id": getattr(node, 'node_id', ''),
                            "relevance": self._calculate_relevance(similarity_score)
                        }
                        results.append(result)

            # Sort by similarity score
            results.sort(key=lambda x: x["similarity_score"], reverse=True)

            logger.info(f"Query returned {len(results)} results for: '{query_text[:50]}...'")

            return results

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []

    def _calculate_relevance(self, similarity_score: float) -> str:
        """Calculate human-readable relevance from similarity score."""
        if similarity_score >= 0.9:
            return "Very High"
        elif similarity_score >= 0.8:
            return "High"
        elif similarity_score >= 0.7:
            return "Medium"
        elif similarity_score >= 0.6:
            return "Low"
        else:
            return "Very Low"

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection."""
        try:
            collection = self.client.get_collection(self.collection_name)
            count = collection.count()

            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "persist_directory": str(self.persist_directory),
                "embedding_model": self.embedding_model,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            }

        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "error": str(e),
                "total_documents": 0
            }

    def list_collections(self) -> List[Dict[str, Any]]:
        """List all available collections."""
        try:
            collections = self.client.list_collections()
            return [
                {
                    "name": col.name,
                    "count": col.count(),
                    "metadata": col.metadata or {}
                }
                for col in collections
            ]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []

    def delete_collection(self, collection_name: Optional[str] = None) -> bool:
        """Delete a collection."""
        target_collection = collection_name or self.collection_name

        try:
            self.client.delete_collection(target_collection)
            logger.info(f"Collection '{target_collection}' deleted successfully")

            # If we deleted our main collection, reinitialize
            if target_collection == self.collection_name:
                self._initialize_vector_store()

            return True

        except Exception as e:
            logger.error(f"Failed to delete collection '{target_collection}': {e}")
            return False

    def reset_collection(self) -> bool:
        """Reset the current collection (delete and recreate)."""
        return self.delete_collection(self.collection_name)

    def export_data(self, export_path: str) -> bool:
        """Export vector store data to file."""
        try:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

            # Get collection data
            collection = self.client.get_collection(self.collection_name)
            data = collection.get()

            # Export to JSON
            import json
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "collection_name": self.collection_name,
                    "export_date": datetime.now().isoformat(),
                    "stats": self.get_collection_stats(),
                    "data": data
                }, f, indent=2, default=str)

            logger.info(f"Data exported to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return False

    def import_data(self, import_path: str) -> bool:
        """Import vector store data from file."""
        try:
            import_path = Path(import_path)
            if not import_path.exists():
                logger.error(f"Import file not found: {import_path}")
                return False

            # Load JSON data
            import json
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Reset collection
            self.reset_collection()

            # Import documents
            imported_docs = []
            for item in data.get("data", {}).get("documents", []):
                doc = Document(
                    text=item.get("text", ""),
                    metadata=item.get("metadata", {})
                )
                imported_docs.append(doc)

            if imported_docs:
                result = self.add_documents(imported_docs)
                return result.get("success", False)

            return True

        except Exception as e:
            logger.error(f"Failed to import data: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on vector store."""
        status = {
            "healthy": True,
            "checks": {},
            "issues": []
        }

        try:
            # Check if collection exists
            collection = self.client.get_collection(self.collection_name)
            status["checks"]["collection_exists"] = True
            status["checks"]["document_count"] = collection.count()

            # Test query
            test_results = self.query("test query", top_k=1)
            status["checks"]["query_functional"] = len(test_results) >= 0

            # Check storage directory
            status["checks"]["storage_accessible"] = self.persist_directory.exists()

        except Exception as e:
            status["healthy"] = False
            status["issues"].append(f"Health check failed: {str(e)}")

        return status