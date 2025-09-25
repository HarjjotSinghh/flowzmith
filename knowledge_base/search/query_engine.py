"""
Semantic search and query engine for the knowledge base.

Provides advanced search capabilities including semantic search,
filtering, and retrieval-augmented generation (RAG) functionality.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path

from llama_index.core import QueryBundle
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import Response

from ..storage.vector_store import VectorStoreManager
from ..ingestion.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)


class KnowledgeQueryEngine:
    """Advanced semantic search engine with RAG capabilities."""

    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        document_processor: DocumentProcessor,
        default_top_k: int = 5,
        similarity_threshold: float = 0.7,
        enable_reranking: bool = True
    ):
        self.vector_store_manager = vector_store_manager
        self.document_processor = document_processor
        self.default_top_k = default_top_k
        self.similarity_threshold = similarity_threshold
        self.enable_reranking = enable_reranking

        # Search statistics
        self.search_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "average_results": 0.0,
            "average_search_time": 0.0,
            "last_search_time": None
        }

        # Initialize query engine
        self._initialize_query_engine()

    def _initialize_query_engine(self):
        """Initialize the LlamaIndex query engine."""
        try:
            # Ensure vector store index is available
            if not self.vector_store_manager.index:
                self.vector_store_manager._rebuild_index()

            if not self.vector_store_manager.index:
                logger.warning("Vector store index not available")
                return

            # Create retriever
            self.retriever = VectorIndexRetriever(
                index=self.vector_store_manager.index,
                similarity_top_k=self.default_top_k
            )

            # Create postprocessor for similarity filtering
            self.postprocessor = SimilarityPostprocessor(
                similarity_cutoff=self.similarity_threshold
            )

            # Create query engine
            self.query_engine = RetrieverQueryEngine.from_args(
                retriever=self.retriever,
                node_postprocessors=[self.postprocessor] if self.enable_reranking else []
            )

            logger.info("Query engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize query engine: {e}")
            self.query_engine = None

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        similarity_threshold: Optional[float] = None,
        include_metadata: bool = True,
        search_type: str = "semantic"
    ) -> Dict[str, Any]:
        """
        Perform semantic search on the knowledge base.

        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Metadata filters to apply
            similarity_threshold: Minimum similarity score
            include_metadata: Whether to include document metadata
            search_type: Type of search ("semantic", "keyword", "hybrid")
        """
        start_time = datetime.now()
        self.search_stats["total_queries"] += 1

        try:
            # Set defaults
            top_k = top_k or self.default_top_k
            similarity_threshold = similarity_threshold or self.similarity_threshold

            logger.info(f"Executing search: '{query[:100]}...' (top_k={top_k}, type={search_type})")

            # Perform search based on type
            if search_type == "semantic":
                results = self._semantic_search(query, top_k, filters, similarity_threshold)
            elif search_type == "keyword":
                results = self._keyword_search(query, top_k, filters)
            elif search_type == "hybrid":
                results = self._hybrid_search(query, top_k, filters, similarity_threshold)
            else:
                raise ValueError(f"Unsupported search type: {search_type}")

            # Process results
            processed_results = self._process_search_results(results, include_metadata)

            # Update statistics
            search_time = (datetime.now() - start_time).total_seconds()
            self._update_search_stats(len(processed_results), search_time, success=True)

            return {
                "success": True,
                "query": query,
                "results": processed_results,
                "total_results": len(processed_results),
                "search_time": search_time,
                "search_type": search_type,
                "filters_applied": filters is not None
            }

        except Exception as e:
            search_time = (datetime.now() - start_time).total_seconds()
            self._update_search_stats(0, search_time, success=False)

            logger.error(f"Search failed: {e}")
            return {
                "success": False,
                "query": query,
                "error": str(e),
                "search_time": search_time
            }

    def _semantic_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        similarity_threshold: float
    ) -> List[NodeWithScore]:
        """Perform semantic search using vector embeddings."""
        if not self.query_engine:
            raise Exception("Query engine not initialized")

        # Create query bundle
        query_bundle = QueryBundle(query_str=query)

        # Retrieve nodes
        nodes = self.retriever.retrieve(query_bundle)

        # Apply filters if provided
        if filters:
            filtered_nodes = []
            for node in nodes:
                if self._apply_filters(node.metadata, filters):
                    filtered_nodes.append(node)
            nodes = filtered_nodes

        # Apply similarity threshold
        filtered_nodes = []
        for node in nodes:
            if hasattr(node, 'score') and node.score >= similarity_threshold:
                filtered_nodes.append(node)

        return filtered_nodes[:top_k]

    def _keyword_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[NodeWithScore]:
        """Perform keyword-based search."""
        # Get all documents from vector store
        all_results = self.vector_store_manager.query(query, top_k=50, similarity_threshold=0.0)

        # Apply keyword matching
        query_terms = [term.lower() for term in query.split()]
        keyword_results = []

        for result in all_results:
            content = result["content"].lower()
            match_count = sum(1 for term in query_terms if term in content)

            if match_count > 0:
                # Create a mock NodeWithScore for keyword results
                node = NodeWithScore(
                    node=result.get("node"),
                    score=match_count / len(query_terms)  # Score based on term matches
                )
                node.metadata = result.get("metadata", {})
                node.text = result["content"]
                keyword_results.append(node)

        # Apply filters
        if filters:
            filtered_results = []
            for node in keyword_results:
                if self._apply_filters(node.metadata, filters):
                    filtered_results.append(node)
            keyword_results = filtered_results

        return sorted(keyword_results, key=lambda x: x.score, reverse=True)[:top_k]

    def _hybrid_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        similarity_threshold: float
    ) -> List[NodeWithScore]:
        """Perform hybrid search combining semantic and keyword approaches."""
        # Get results from both methods
        semantic_results = self._semantic_search(query, top_k * 2, filters, similarity_threshold)
        keyword_results = self._keyword_search(query, top_k * 2, filters)

        # Combine and deduplicate results
        combined_results = {}

        # Add semantic results with higher weight
        for node in semantic_results:
            content_hash = hash(node.text)
            combined_results[content_hash] = {
                "node": node,
                "combined_score": node.score * 0.7  # 70% weight for semantic
            }

        # Add keyword results, boosting if already in semantic results
        for node in keyword_results:
            content_hash = hash(node.text)
            if content_hash in combined_results:
                # Boost existing result
                combined_results[content_hash]["combined_score"] += node.score * 0.3
            else:
                # Add new result
                combined_results[content_hash] = {
                    "node": node,
                    "combined_score": node.score * 0.3  # 30% weight for keyword
                }

        # Sort by combined score and return top results
        sorted_results = sorted(
            combined_results.values(),
            key=lambda x: x["combined_score"],
            reverse=True
        )

        return [item["node"] for item in sorted_results[:top_k]]

    def _apply_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply metadata filters to search results."""
        for key, value in filters.items():
            if key not in metadata:
                return False

            metadata_value = metadata[key]

            if isinstance(value, dict):
                # Handle operators like $eq, $ne, $in, etc.
                for op, filter_value in value.items():
                    if op == "$eq" and metadata_value != filter_value:
                        return False
                    elif op == "$ne" and metadata_value == filter_value:
                        return False
                    elif op == "$in" and metadata_value not in filter_value:
                        return False
                    elif op == "$nin" and metadata_value in filter_value:
                        return False
                    elif op == "$gt" and not (metadata_value > filter_value):
                        return False
                    elif op == "$lt" and not (metadata_value < filter_value):
                        return False
                    elif op == "$gte" and not (metadata_value >= filter_value):
                        return False
                    elif op == "$lte" and not (metadata_value <= filter_value):
                        return False
            else:
                # Direct equality check
                if metadata_value != value:
                    return False

        return True

    def _process_search_results(
        self,
        nodes: List[NodeWithScore],
        include_metadata: bool
    ) -> List[Dict[str, Any]]:
        """Process search nodes into standardized format."""
        results = []

        for i, node in enumerate(nodes):
            result = {
                "rank": i + 1,
                "content": node.text,
                "similarity_score": getattr(node, 'score', 0.0),
                "relevance": self._calculate_relevance(getattr(node, 'score', 0.0))
            }

            if include_metadata:
                result["metadata"] = node.metadata or {}
                result["node_id"] = getattr(node, 'node_id', f"result_{i}")

            results.append(result)

        return results

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

    def _update_search_stats(self, result_count: int, search_time: float, success: bool):
        """Update search statistics."""
        if success:
            self.search_stats["successful_queries"] += 1
        else:
            self.search_stats["failed_queries"] += 1

        # Update average results
        total_queries = self.search_stats["successful_queries"]
        if total_queries > 0:
            current_avg = self.search_stats["average_results"]
            self.search_stats["average_results"] = (
                (current_avg * (total_queries - 1) + result_count) / total_queries
            )

        # Update average search time
        if total_queries > 0:
            current_avg_time = self.search_stats["average_search_time"]
            self.search_stats["average_search_time"] = (
                (current_avg_time * (total_queries - 1) + search_time) / total_queries
            )

        self.search_stats["last_search_time"] = datetime.now().isoformat()

    def get_search_stats(self) -> Dict[str, Any]:
        """Get comprehensive search statistics."""
        return {
            **self.search_stats,
            "query_engine_healthy": self.query_engine is not None,
            "vector_store_stats": self.vector_store_manager.get_collection_stats(),
            "default_top_k": self.default_top_k,
            "similarity_threshold": self.similarity_threshold,
            "reranking_enabled": self.enable_reranking
        }

    def suggest_related_queries(self, query: str, max_suggestions: int = 5) -> List[str]:
        """Generate related query suggestions based on search results."""
        try:
            # Get search results for the original query
            results = self.search(query, top_k=10, search_type="semantic")

            if not results["success"] or not results["results"]:
                return []

            # Extract key terms from results
            all_text = " ".join([result["content"] for result in results["results"]])

            # Simple keyword extraction (in production, use more sophisticated NLP)
            words = all_text.lower().split()
            word_freq = {}

            for word in words:
                if len(word) > 3 and word.isalpha():  # Ignore short words and punctuation
                    word_freq[word] = word_freq.get(word, 0) + 1

            # Get most frequent words that aren't in original query
            query_words = set(query.lower().split())
            suggestions = []

            for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True):
                if word not in query_words and len(suggestions) < max_suggestions:
                    suggestions.append(f"{query} {word}")

            return suggestions[:max_suggestions]

        except Exception as e:
            logger.error(f"Failed to generate query suggestions: {e}")
            return []

    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of the query engine."""
        status = {
            "healthy": True,
            "checks": {},
            "issues": []
        }

        try:
            # Check query engine initialization
            status["checks"]["query_engine_initialized"] = self.query_engine is not None

            # Check vector store health
            vector_store_health = self.vector_store_manager.health_check()
            status["checks"]["vector_store_healthy"] = vector_store_health.get("healthy", False)

            # Test basic search functionality
            test_query = "test query"
            test_results = self.search(test_query, top_k=1)
            status["checks"]["search_functional"] = test_results.get("success", False)

            # Check if we have any documents
            collection_stats = self.vector_store_manager.get_collection_stats()
            status["checks"]["has_documents"] = collection_stats.get("total_documents", 0) > 0

            # Overall health determination
            if not all(status["checks"].values()):
                status["healthy"] = False
                failed_checks = [check for check, passed in status["checks"].items() if not passed]
                status["issues"] = [f"Failed check: {check}" for check in failed_checks]

        except Exception as e:
            status["healthy"] = False
            status["issues"].append(f"Health check error: {str(e)}")

        return status