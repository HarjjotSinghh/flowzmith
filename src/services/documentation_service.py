"""
Documentation indexing and search service for Flowzmith.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import text
import re
from datetime import datetime

from ..models import (
    DocumentationKnowledgeBase,
    ContentType
)
from ..config import get_settings
from .firecrawl_service import FirecrawlService

logger = logging.getLogger(__name__)

# Try to import ChromaDB for vector search
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class DocumentSource(str, Enum):
    """Documentation sources."""
    OFFICIAL_FLOW_DOCS = "OFFICIAL_FLOW_DOCS"
    OFFICIAL_CADENCE_DOCS = "OFFICIAL_CADENCE_DOCS"
    COMMUNITY_EXAMPLES = "COMMUNITY_EXAMPLES"
    CUSTOM_DOCUMENTATION = "CUSTOM_DOCUMENTATION"


class DocumentationService:
    """Service for managing indexed documentation knowledge base."""

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.settings = get_settings()
        self.chroma_client = None
        self.vector_collection = None
        self.firecrawl_service = FirecrawlService()
        self._initialize_vector_db()

    def _initialize_vector_db(self):
        """Initialize vector database if available."""
        # Check if enable_vector_search exists, default to True if ChromaDB is available
        enable_vector_search = getattr(self.settings, 'enable_vector_search', CHROMADB_AVAILABLE)
        if CHROMADB_AVAILABLE and enable_vector_search:
            try:
                # Initialize ChromaDB client with new API
                import chromadb
                self.chroma_client = chromadb.PersistentClient(path=self.settings.vector_db_path)
                
                # Get or create collection
                self.vector_collection = self.chroma_client.get_or_create_collection(
                    name="flow_documentation",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("Vector database initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize vector database: {e}")
                self.chroma_client = None
        else:
            logger.warning("Vector search disabled - ChromaDB not available")

    def index_official_documentation(self) -> int:
        """Index official Flow and Cadence documentation."""
        indexed_count = 0

        # Index Flow documentation
        indexed_count += self._index_flow_docs()

        # Index Cadence documentation
        indexed_count += self._index_cadence_docs()

        logger.info(f"Indexed {indexed_count} documentation entries")
        return indexed_count

    def _index_flow_docs(self) -> int:
        """Index Flow blockchain documentation."""
        count = 0

        # Simulate indexing Flow documentation
        # In a real implementation, this would scrape or fetch from official docs
        flow_docs = [
            {
                "title": "Flow Accounts",
                "content_type": ContentType.LANGUAGE_SPEC,
                "content": """
                Flow accounts are the foundation of user interaction with the blockchain.
                Each account has a unique address and can store contracts, assets, and keys.

                Key concepts:
                - Account creation requires payment
                - Accounts can have multiple keys with different weights
                - Account contracts are stored in the /storage path
                - Account assets are stored in /storage path
                """,
                "source": DocumentSource.OFFICIAL_FLOW_DOCS.value,
                "version": "1.0.0"
            },
            {
                "title": "Flow Transactions",
                "content_type": ContentType.API_REFERENCE,
                "content": """
                Flow transactions are used to execute smart contract code and update the blockchain state.

                Transaction structure:
                - Prepare phase: Access signer accounts
                - Pre-execute phase: Validate transaction
                - Execute phase: Execute transaction logic
                - Post-execute phase: Finalize changes

                Transaction types:
                - Script transactions: Read-only operations
                - Account transactions: Modify account state
                - Contract transactions: Deploy or update contracts
                """,
                "source": DocumentSource.OFFICIAL_FLOW_DOCS.value,
                "version": "1.0.0"
            },
            {
                "title": "Flow Smart Contracts",
                "content_type": ContentType.LANGUAGE_SPEC,
                "content": """
                Flow smart contracts are written in Cadence and deployed to accounts.

                Contract structure:
                - Contract declaration with optional parameters
                - Resource definitions (NFTs, Fungible Tokens)
                - Public and private interfaces
                - Event definitions

                Best practices:
                - Use proper access control (pub, priv, access)
                - Implement proper resource lifecycle management
                - Use interfaces for composability
                - Include comprehensive error handling
                """,
                "source": DocumentSource.OFFICIAL_FLOW_DOCS.value,
                "version": "1.0.0"
            }
        ]

        for doc in flow_docs:
            doc_entry = DocumentationKnowledgeBase(
                source=doc["source"],
                title=doc["title"],
                content_type=doc["content_type"],
                content=doc["content"],
                version=doc["version"]
            )
            self.db_session.add(doc_entry)
            count += 1

        return count

    def _index_cadence_docs(self) -> int:
        """Index Cadence language documentation."""
        count = 0

        # Simulate indexing Cadence documentation
        cadence_docs = [
            {
                "title": "Cadence Resources",
                "content_type": ContentType.LANGUAGE_SPEC,
                "content": """
                Resources are the primary way to define assets and state in Cadence.

                Resource characteristics:
                - Resources can only exist in account storage
                - Resources cannot be copied
                - Resources must be explicitly moved or destroyed
                - Resources can contain other resources

                Resource lifecycle:
                1. Create resource using create() function
                2. Move resource to account storage
                3. Borrow references for interaction
                4. Destroy or move when no longer needed

                Example:
                pub resource NFT {
                    pub let id: UInt64
                    pub let metadata: {String: String}

                    init(id: UInt64, metadata: {String: String}) {
                        self.id = id
                        self.metadata = metadata
                    }

                    destroy() {
                        // Cleanup logic
                    }
                }
                """,
                "source": DocumentSource.OFFICIAL_CADENCE_DOCS.value,
                "version": "1.0.0"
            },
            {
                "title": "Cadence Capabilities",
                "content_type": ContentType.LANGUAGE_SPEC,
                "content": """
                Capabilities control access to resources and objects in account storage.

                Types of capabilities:
                - Public capabilities: Anyone can access
                - Private capabilities: Only account owner can access
                - Linked capabilities: Connected to specific resources

                Capability management:
                - Create capabilities using the 'link' keyword
                - Get capabilities using the 'getCapability' function
                - Borrow references through capabilities

                Example:
                // Create public capability
                account.link<&NFT{NFTPublic}>(/public/NFT, target: /storage/NFTCollection)

                // Get capability
                let cap = account.getCapability<&NFT{NFTPublic}>(/public/NFT)
                """,
                "source": DocumentSource.OFFICIAL_CADENCE_DOCS.value,
                "version": "1.0.0"
            },
            {
                "title": "Cadence Events",
                "content_type": ContentType.TUTORIAL,
                "content": """
                Events are used to emit information from smart contracts for external systems.

                Event characteristics:
                - Events are emitted from contracts and transactions
                - Events can contain any serializable data
                - Events are stored on-chain and can be queried

                Event best practices:
                - Use descriptive event names
                - Include all relevant data in event payload
                - Emit events at key state changes
                - Use events for off-chain integration

                Example:
                pub event NFTMinted(id: UInt64, to: Address)
                pub event NFTTransferred(id: UInt64, from: Address, to: Address)

                // Emit event
                emit NFTMinted(id: newNFT.id, to: self.account.address)
                """,
                "source": DocumentSource.OFFICIAL_CADENCE_DOCS.value,
                "version": "1.0.0"
            }
        ]

        for doc in cadence_docs:
            doc_entry = DocumentationKnowledgeBase(
                source=doc["source"],
                title=doc["title"],
                content_type=doc["content_type"],
                content=doc["content"],
                version=doc["version"]
            )
            self.db_session.add(doc_entry)
            count += 1

        return count

    def search_documentation(
        self,
        query: str,
        content_type: Optional[ContentType] = None,
        limit: int = 10
    ) -> List[DocumentationKnowledgeBase]:
        """Search documentation database."""
        try:
            # Base query
            search_query = self.db_session.query(DocumentationKnowledgeBase)

            # Filter by content type if specified
            if content_type:
                search_query = search_query.filter(
                    DocumentationKnowledgeBase.content_type == content_type
                )

            # Text search using database-specific full-text search
            if hasattr(self.db_session.bind, 'dialect'):
                dialect_name = self.db_session.bind.dialect.name
                if dialect_name == 'postgresql':
                    # PostgreSQL full-text search
                    search_query = search_query.filter(
                        text("to_tsvector('english', content || ' ' || title) @@ to_tsquery('english', :query)")
                    ).params(query=self._format_tsquery(query))
                elif dialect_name == 'sqlite':
                    # SQLite LIKE search
                    search_query = search_query.filter(
                        DocumentationKnowledgeBase.content.ilike(f"%{query}%") |
                        DocumentationKnowledgeBase.title.ilike(f"%{query}%")
                    )

            results = search_query.order_by(
                DocumentationKnowledgeBase.last_updated.desc()
            ).limit(limit).all()

            logger.info(f"Documentation search for '{query}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Documentation search failed: {e}")
            return []

    def _format_tsquery(self, query: str) -> str:
        """Format query for PostgreSQL full-text search."""
        # Simple format - replace spaces with & and clean up
        formatted = re.sub(r'\s+', ' & ', query.strip())
        return formatted

    def semantic_search(
        self,
        query: str,
        limit: int = 10
    ) -> List[Tuple[DocumentationKnowledgeBase, float]]:
        """Perform semantic search using vector embeddings."""
        if not self.vector_collection:
            logger.warning("Vector search not available")
            return []

        try:
            # Generate query embedding (in production, use actual embedding model)
            query_embedding = self._generate_query_embedding(query)

            # Search vector collection
            results = self.vector_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )

            # Map results to documentation entries
            search_results = []
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    doc = self.db_session.query(DocumentationKnowledgeBase).filter(
                        DocumentationKnowledgeBase.id == doc_id
                    ).first()

                    if doc:
                        distance = results['distances'][0][i]
                        similarity_score = 1 - distance  # Convert distance to similarity
                        search_results.append((doc, similarity_score))

            logger.info(f"Semantic search for '{query}' returned {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    def _generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query."""
        # Simplified embedding generation
        # In production, use actual embedding models like sentence-transformers
        words = query.lower().split()
        embedding = [0.0] * 384  # Standard embedding size

        for i, word in enumerate(words[:384]):
            # Simple hash-based embedding (for demonstration)
            hash_val = sum(ord(c) for c in word) % 1000 / 1000.0
            embedding[i] = hash_val

        return embedding

    def get_relevant_documentation(
        self,
        contract_requirements: str,
        content_types: Optional[List[ContentType]] = None
    ) -> List[DocumentationKnowledgeBase]:
        """Get relevant documentation for contract generation."""
        relevant_docs = []

        # Extract key terms from requirements
        key_terms = self._extract_key_terms(contract_requirements)

        # Search for each key term
        for term in key_terms:
            docs = self.search_documentation(
                term,
                content_type=content_types[0] if content_types else None,
                limit=5
            )
            relevant_docs.extend(docs)

        # Remove duplicates and limit results
        unique_docs = list({doc.id: doc for doc in relevant_docs}.values())
        return unique_docs[:10]

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text."""
        # Simple keyword extraction
        flow_keywords = [
            'resource', 'capability', 'contract', 'transaction', 'account',
            'NFT', 'fungible', 'token', 'event', 'struct', 'interface',
            'public', 'private', 'access', 'storage', 'let', 'var'
        ]

        cadence_keywords = [
            'pub', 'priv', 'init', 'destroy', 'prepare', 'execute',
            'borrow', 'link', 'getCapability', 'emit', 'create'
        ]

        all_keywords = flow_keywords + cadence_keywords

        # Find keywords in text
        found_terms = []
        text_lower = text.lower()

        for keyword in all_keywords:
            if keyword.lower() in text_lower:
                found_terms.append(keyword)

        return found_terms

    def add_custom_documentation(
        self,
        title: str,
        content: str,
        content_type: ContentType,
        source: str = DocumentSource.CUSTOM_DOCUMENTATION.value
    ) -> DocumentationKnowledgeBase:
        """Add custom documentation entry."""
        doc_entry = DocumentationKnowledgeBase(
            source=source,
            title=title,
            content_type=content_type,
            content=content
        )

        self.db_session.add(doc_entry)
        self.db_session.commit()

        logger.info(f"Added custom documentation: {title}")
        return doc_entry

    def update_documentation_embeddings(self):
        """Update vector embeddings for all documentation entries."""
        if not self.vector_collection:
            logger.warning("Vector search not available")
            return

        try:
            # Get all documentation entries
            docs = self.db_session.query(DocumentationKnowledgeBase).all()

            # Update embeddings for each document
            for doc in docs:
                embedding = self._generate_query_embedding(doc.content)

                # Store in vector collection
                self.vector_collection.add(
                    ids=[str(doc.id)],
                    embeddings=[embedding],
                    metadatas=[{
                        "title": doc.title,
                        "content_type": doc.content_type.value,
                        "source": doc.source
                    }]
                )

            logger.info(f"Updated embeddings for {len(docs)} documentation entries")

        except Exception as e:
            logger.error(f"Failed to update documentation embeddings: {e}")

    def get_documentation_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed documentation."""
        try:
            total_docs = self.db_session.query(DocumentationKnowledgeBase).count()

            # Count by content type
            content_type_counts = {}
            for content_type in ContentType:
                count = self.db_session.query(DocumentationKnowledgeBase).filter(
                    DocumentationKnowledgeBase.content_type == content_type
                ).count()
                content_type_counts[content_type.value] = count

            # Count by source
            source_counts = {}
            sources = self.db_session.query(
                DocumentationKnowledgeBase.source,
                text('count(*)').label('count')
            ).group_by(DocumentationKnowledgeBase.source).all()

            for source, count in sources:
                source_counts[source] = count

            return {
                "total_documents": total_docs,
                "content_type_distribution": content_type_counts,
                "source_distribution": source_counts,
                "vector_search_enabled": CHROMADB_AVAILABLE and self.vector_collection is not None
            }

        except Exception as e:
            logger.error(f"Failed to get documentation stats: {e}")
            return {}

    def crawl_and_index_cadence_docs(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Crawl and index real Cadence documentation using Firecrawl."""
        if not self.firecrawl_service.is_available():
            logger.error("Firecrawl service is not available")
            return {"success": False, "error": "Firecrawl service unavailable"}

        try:
            # Check if we already have recent Cadence docs (unless force refresh)
            if not force_refresh:
                recent_docs = self.db_session.query(DocumentationKnowledgeBase).filter(
                    DocumentationKnowledgeBase.source == DocumentSource.OFFICIAL_CADENCE_DOCS.value,
                    DocumentationKnowledgeBase.last_updated >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                ).count()
                
                if recent_docs > 0:
                    logger.info("Recent Cadence documentation already indexed today")
                    return {"success": True, "message": "Documentation already up to date", "pages_indexed": recent_docs}

            # Crawl Cadence documentation
            logger.info("Starting Cadence documentation crawl...")
            crawl_results = self.firecrawl_service.crawl_cadence_documentation()
            
            if not crawl_results or crawl_results.get("successful_crawls", 0) == 0:
                return {"success": False, "error": "Failed to crawl Cadence documentation"}

            pages_indexed = 0
            pages_failed = 0

            # Process each crawled source
            for url, source_data in crawl_results.get("sources", {}).items():
                if source_data.get("status") == "success" and source_data.get("data"):
                    # Process each page in this source
                    for page_data in source_data.get("data", []):
                        try:
                            # Extract content from page data
                            content = page_data.get("markdown", "")
                            metadata = page_data.get("metadata", {})
                            title = metadata.get("title", url.split("/")[-1])
                            
                            if content and len(content.strip()) > 100:  # Only index substantial content
                                # Determine content type based on URL and content
                                content_type = self._determine_content_type(url, content)
                                
                                # Check if this page already exists
                                existing_doc = self.db_session.query(DocumentationKnowledgeBase).filter(
                                    DocumentationKnowledgeBase.source == DocumentSource.OFFICIAL_CADENCE_DOCS.value,
                                    DocumentationKnowledgeBase.title == title
                                ).first()

                                if existing_doc:
                                    # Update existing document
                                    existing_doc.content = content
                                    existing_doc.last_updated = datetime.now()
                                    existing_doc.metadata = {"url": url, "crawled_at": datetime.now().isoformat()}
                                else:
                                    # Create new document
                                    doc_entry = DocumentationKnowledgeBase(
                                        source=DocumentSource.OFFICIAL_CADENCE_DOCS.value,
                                        title=title,
                                        content_type=content_type,
                                        content=content,
                                        version="latest",
                                        metadata={"url": url, "crawled_at": datetime.now().isoformat()}
                                    )
                                    self.db_session.add(doc_entry)
                                
                                pages_indexed += 1
                            else:
                                logger.warning(f"Skipping page with insufficient content: {url}")
                                pages_failed += 1

                        except Exception as e:
                            logger.error(f"Error processing page {url}: {e}")
                            pages_failed += 1

            # Commit all changes
            self.db_session.commit()
            
            # Update vector embeddings for new content
            if pages_indexed > 0:
                self.update_documentation_embeddings()

            logger.info(f"Crawl completed: {pages_indexed} pages indexed, {pages_failed} pages failed")
            
            return {
                "success": True,
                "pages_indexed": pages_indexed,
                "pages_failed": pages_failed,
                "total_pages": pages_indexed + pages_failed
            }

        except Exception as e:
            logger.error(f"Error during Cadence documentation crawl: {e}")
            self.db_session.rollback()
            return {"success": False, "error": str(e)}

    def _determine_content_type(self, url: str, content: str) -> ContentType:
        """Determine content type based on URL and content analysis."""
        url_lower = url.lower()
        content_lower = content.lower()

        # Check URL patterns
        if "tutorial" in url_lower or "guide" in url_lower:
            return ContentType.TUTORIAL
        elif "example" in url_lower:
            return ContentType.CODE_EXAMPLE
        elif "api" in url_lower or "reference" in url_lower:
            return ContentType.API_REFERENCE
        elif "language" in url_lower or "spec" in url_lower:
            return ContentType.LANGUAGE_SPEC

        # Check content patterns
        if "example" in content_lower and "```" in content:
            return ContentType.CODE_EXAMPLE
        elif "tutorial" in content_lower or "step" in content_lower:
            return ContentType.TUTORIAL
        elif "function" in content_lower or "method" in content_lower:
            return ContentType.API_REFERENCE
        else:
            return ContentType.LANGUAGE_SPEC

    def scrape_single_page(self, url: str) -> Dict[str, Any]:
        """Scrape a single documentation page and optionally index it."""
        if not self.firecrawl_service.is_available():
            return {"success": False, "error": "Firecrawl service unavailable"}

        try:
            result = self.firecrawl_service.scrape_url(url)
            
            if result and result.get("status") == "success":
                return {
                    "success": True,
                    "data": result.get("data", {}),
                    "url": url
                }
            else:
                error_msg = result.get("error", "Failed to scrape page") if result else "No data returned"
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"Error scraping page {url}: {e}")
            return {"success": False, "error": str(e)}

    def index_scraped_content(
        self,
        url: str,
        title: str,
        content: str,
        source: str = DocumentSource.CUSTOM_DOCUMENTATION.value,
        content_type: Optional[ContentType] = None
    ) -> DocumentationKnowledgeBase:
        """Index scraped content into the knowledge base."""
        if not content_type:
            content_type = self._determine_content_type(url, content)

        doc_entry = DocumentationKnowledgeBase(
            source=source,
            title=title,
            content_type=content_type,
            content=content,
            version="latest",
            metadata={"url": url, "scraped_at": datetime.now().isoformat()}
        )

        self.db_session.add(doc_entry)
        self.db_session.commit()

        logger.info(f"Indexed scraped content: {title} from {url}")
        return doc_entry

    def get_crawl_status(self, crawl_id: str) -> Dict[str, Any]:
        """Get the status of a Firecrawl crawl job."""
        if not self.firecrawl_service.is_available():
            return {"success": False, "error": "Firecrawl service unavailable"}

        try:
            return self.firecrawl_service.get_crawl_status(crawl_id)
        except Exception as e:
            logger.error(f"Error getting crawl status: {e}")
            return {"success": False, "error": str(e)}