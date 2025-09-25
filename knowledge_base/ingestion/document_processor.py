"""
Document processing system for knowledge base ingestion.

Handles loading, parsing, and chunking documents from various formats
including PDF, Word, text files, and code files.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file import (
    PDFReader,
    DocxReader,
    MarkdownReader,
    PyMuPDFReader
)
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.schema import BaseNode

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Advanced document processor with multi-format support and intelligent chunking."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        include_metadata: bool = True,
        supported_formats: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.include_metadata = include_metadata

        # Initialize text splitter
        self.text_splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Supported file formats
        self.supported_formats = supported_formats or [
            ".pdf", ".docx", ".doc", ".txt", ".md", ".py", ".js", ".sol", ".cdc"
        ]

        # Initialize readers
        self.readers = {
            ".pdf": PyMuPDFReader(),
            ".docx": DocxReader(),
            ".doc": DocxReader(),
            ".md": MarkdownReader()
        }

    def process_directory(self, directory_path: Union[str, Path]) -> List[Document]:
        """Process all supported documents in a directory."""
        directory_path = Path(directory_path)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        documents = []
        processed_files = []
        skipped_files = []

        logger.info(f"Starting document processing for directory: {directory_path}")

        for file_path in directory_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    file_docs = self.process_file(file_path)
                    documents.extend(file_docs)
                    processed_files.append(str(file_path))
                    logger.info(f"Successfully processed: {file_path}")
                except Exception as e:
                    skipped_files.append(str(file_path))
                    logger.error(f"Failed to process {file_path}: {e}")

        logger.info(f"Processing complete. Processed: {len(processed_files)}, Skipped: {len(skipped_files)}")
        logger.info(f"Total documents generated: {len(documents)}")

        return documents

    def process_file(self, file_path: Union[str, Path]) -> List[Document]:
        """Process a single file and return chunked documents."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = file_path.suffix.lower()
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")

        logger.info(f"Processing file: {file_path}")

        # Load document based on file type
        if file_extension == ".txt" or file_extension in [".py", ".js", ".sol", ".cdc"]:
            # For text and code files, use simple reader
            reader = SimpleDirectoryReader(input_files=[str(file_path)])
            documents = reader.load_data()
        else:
            # For other formats, use specific readers
            reader = self.readers.get(file_extension)
            if reader and hasattr(reader, 'load_data'):
                documents = reader.load_data(file_path)
            else:
                # Fallback to simple directory reader
                reader = SimpleDirectoryReader(input_files=[str(file_path)])
                documents = reader.load_data()

        if not documents:
            logger.warning(f"No documents extracted from: {file_path}")
            return []

        # Add metadata to documents
        for doc in documents:
            self._enrich_document_metadata(doc, file_path)

        # Split documents into chunks
        chunked_documents = self._chunk_documents(documents)

        return chunked_documents

    def process_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Process raw text content into chunked documents."""
        # Create base document
        doc = Document(
            text=text,
            metadata=metadata or {}
        )

        # Add processing metadata
        doc.metadata.update({
            "processing_date": datetime.now().isoformat(),
            "source_type": "raw_text",
            "chunk_count": 0  # Will be updated after chunking
        })

        # Split into chunks
        chunked_docs = self._chunk_documents([doc])

        return chunked_docs

    def _chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into optimized chunks for vector storage."""
        chunked_docs = []

        for doc in documents:
            try:
                # Split document into nodes
                nodes = self.text_splitter.get_nodes_from_documents([doc])

                # Convert nodes back to documents with enhanced metadata
                for i, node in enumerate(nodes):
                    chunk_doc = Document(
                        text=node.text,
                        metadata={
                            **doc.metadata,
                            "chunk_index": i,
                            "total_chunks": len(nodes),
                            "chunk_text": node.text[:100] + "..." if len(node.text) > 100 else node.text,
                            "processing_date": datetime.now().isoformat()
                        }
                    )
                    chunked_docs.append(chunk_doc)

            except Exception as e:
                logger.error(f"Error chunking document: {e}")
                # Add the original document as a single chunk if chunking fails
                chunk_doc = Document(
                    text=doc.text,
                    metadata={
                        **doc.metadata,
                        "chunk_index": 0,
                        "total_chunks": 1,
                        "chunk_text": doc.text[:100] + "..." if len(doc.text) > 100 else doc.text,
                        "processing_date": datetime.now().isoformat(),
                        "chunking_error": str(e)
                    }
                )
                chunked_docs.append(chunk_doc)

        return chunked_docs

    def _enrich_document_metadata(self, document: Document, file_path: Path):
        """Add comprehensive metadata to document."""
        base_metadata = {
            "source_file": str(file_path),
            "file_name": file_path.name,
            "file_extension": file_path.suffix.lower(),
            "file_size": file_path.stat().st_size,
            "processing_date": datetime.now().isoformat(),
            "chunk_count": 0,
            "document_type": self._detect_document_type(file_path.suffix.lower())
        }

        # Extract additional metadata based on file type
        if file_path.suffix.lower() in [".py", ".js", ".sol", ".cdc"]:
            base_metadata.update({
                "language": self._detect_programming_language(file_path.suffix.lower()),
                "is_code": True
            })

        # Merge with existing metadata
        document.metadata.update(base_metadata)

    def _detect_document_type(self, file_extension: str) -> str:
        """Detect document type based on file extension."""
        type_mapping = {
            ".pdf": "PDF Document",
            ".docx": "Word Document",
            ".doc": "Word Document (Legacy)",
            ".txt": "Text File",
            ".md": "Markdown Document",
            ".py": "Python Source Code",
            ".js": "JavaScript Source Code",
            ".sol": "Solidity Smart Contract",
            ".cdc": "CADENCE Smart Contract"
        }
        return type_mapping.get(file_extension, "Unknown Document")

    def _detect_programming_language(self, file_extension: str) -> str:
        """Detect programming language based on file extension."""
        lang_mapping = {
            ".py": "Python",
            ".js": "JavaScript",
            ".sol": "Solidity",
            ".cdc": "CADENCE"
        }
        return lang_mapping.get(file_extension, "Unknown")

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about document processing."""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "supported_formats": self.supported_formats,
            "include_metadata": self.include_metadata,
            "text_splitter_type": type(self.text_splitter).__name__
        }

    def validate_document_quality(self, documents: List[Document]) -> Dict[str, Any]:
        """Validate processed documents and return quality metrics."""
        if not documents:
            return {"valid": False, "error": "No documents provided"}

        stats = {
            "total_documents": len(documents),
            "total_chunks": 0,
            "average_chunk_length": 0,
            "empty_chunks": 0,
            "very_small_chunks": 0,  # chunks < 50 characters
            "very_large_chunks": 0,  # chunks > 2000 characters
            "documents_with_metadata": 0,
            "missing_source_files": 0
        }

        total_length = 0

        for doc in documents:
            text_length = len(doc.text.strip())
            total_length += text_length

            if text_length == 0:
                stats["empty_chunks"] += 1
            elif text_length < 50:
                stats["very_small_chunks"] += 1
            elif text_length > 2000:
                stats["very_large_chunks"] += 1

            if doc.metadata:
                stats["documents_with_metadata"] += 1
                if "source_file" not in doc.metadata:
                    stats["missing_source_files"] += 1

            if "chunk_index" in doc.metadata:
                stats["total_chunks"] = max(stats["total_chunks"], doc.metadata.get("total_chunks", 0))

        if stats["total_documents"] > 0:
            stats["average_chunk_length"] = total_length / stats["total_documents"]

        # Determine overall quality
        quality_issues = []
        if stats["empty_chunks"] > 0:
            quality_issues.append(f"{stats['empty_chunks']} empty chunks")
        if stats["very_small_chunks"] > stats["total_documents"] * 0.1:
            quality_issues.append("Too many very small chunks")
        if stats["very_large_chunks"] > stats["total_documents"] * 0.1:
            quality_issues.append("Too many very large chunks")
        if stats["missing_source_files"] > stats["total_documents"] * 0.5:
            quality_issues.append("Many documents missing source file metadata")

        stats["valid"] = len(quality_issues) == 0
        stats["quality_issues"] = quality_issues
        stats["quality_score"] = max(0, 100 - len(quality_issues) * 20)

        return stats