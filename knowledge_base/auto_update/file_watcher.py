"""
Auto-updating knowledge base with file system monitoring.

Uses watchdog to monitor directories for new/modified documents
and automatically updates the vector store.
"""

import os
import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ..ingestion.document_processor import DocumentProcessor
from ..storage.vector_store import VectorStoreManager

logger = logging.getLogger(__name__)


class NewFileHandler(FileSystemEventHandler):
    """Handle file system events for auto-updating knowledge base."""

    def __init__(self, knowledge_base_updater, debounce_seconds: int = 5):
        self.knowledge_base_updater = knowledge_base_updater
        self.debounce_seconds = debounce_seconds
        self.pending_files = {}
        self.last_processed = {}
        self.processing_lock = threading.Lock()

    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            self._schedule_file_processing(event.src_path, "created")

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            self._schedule_file_processing(event.src_path, "modified")

    def on_moved(self, event):
        """Handle file move events."""
        if not event.is_directory:
            self._schedule_file_processing(event.dest_path, "moved")

    def _schedule_file_processing(self, file_path: str, event_type: str):
        """Schedule file processing with debouncing."""
        file_path = Path(file_path)

        # Check if file extension is supported
        supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md', '.py', '.js', '.sol', '.cdc'}
        if file_path.suffix.lower() not in supported_extensions:
            return

        # Check if file was recently processed (debounce)
        current_time = datetime.now()
        if file_path in self.last_processed:
            time_diff = (current_time - self.last_processed[file_path]).total_seconds()
            if time_diff < self.debounce_seconds:
                return

        with self.processing_lock:
            self.pending_files[file_path] = {
                "event_type": event_type,
                "scheduled_time": current_time
            }

        # Log the event
        logger.info(f"File {event_type}: {file_path}")

        # Schedule processing
        threading.Timer(
            self.debounce_seconds,
            self._process_pending_file,
            args=[file_path]
        ).start()

    def _process_pending_file(self, file_path: Path):
        """Process a pending file."""
        with self.processing_lock:
            if file_path not in self.pending_files:
                return

            file_info = self.pending_files.pop(file_path)
            self.last_processed[file_path] = datetime.now()

        try:
            self.knowledge_base_updater.process_file_update(file_path, file_info["event_type"])
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")


class KnowledgeBaseUpdater:
    """Main class for auto-updating knowledge base."""

    def __init__(
        self,
        watch_directories: List[str],
        vector_store_manager: VectorStoreManager,
        document_processor: DocumentProcessor,
        collection_name: str = "smart_contracts_auto_update",
        debounce_seconds: int = 10,
        max_retries: int = 3
    ):
        self.watch_directories = [Path(d) for d in watch_directories]
        self.vector_store_manager = vector_store_manager
        self.document_processor = document_processor
        self.collection_name = collection_name
        self.debounce_seconds = debounce_seconds
        self.max_retries = max_retries

        # Initialize observers
        self.observers = []
        self.running = False

        # Processing queue and stats
        self.processing_queue = []
        self.processing_stats = {
            "files_processed": 0,
            "files_failed": 0,
            "last_update": None,
            "total_processing_time": 0.0
        }

        # Create dedicated collection for auto-updates
        self._setup_auto_update_collection()

    def _setup_auto_update_collection(self):
        """Set up dedicated collection for auto-updated documents."""
        try:
            # Check if collection exists
            collections = self.vector_store_manager.list_collections()
            collection_names = [col["name"] for col in collections]

            if self.collection_name not in collection_names:
                # Create new collection by attempting to get it
                self.vector_store_manager.client.get_or_create_collection(self.collection_name)
                logger.info(f"Created auto-update collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to setup auto-update collection: {e}")

    def start_watching(self):
        """Start watching directories for file changes."""
        if self.running:
            logger.warning("File watcher is already running")
            return

        self.running = True

        # Create file event handler
        event_handler = NewFileHandler(self, self.debounce_seconds)

        # Set up observers for each directory
        for directory in self.watch_directories:
            if not directory.exists():
                logger.warning(f"Watch directory does not exist: {directory}")
                continue

            observer = Observer()
            observer.schedule(event_handler, str(directory), recursive=True)
            observer.start()
            self.observers.append(observer)

            logger.info(f"Started watching directory: {directory}")

        if not self.observers:
            logger.error("No directories to watch")
            return

        logger.info(f"Auto-update knowledge base started with {len(self.observers)} observers")

    def stop_watching(self):
        """Stop watching directories."""
        if not self.running:
            return

        self.running = False

        for observer in self.observers:
            observer.stop()
            observer.join()

        self.observers.clear()
        logger.info("Auto-update knowledge base stopped")

    def process_file_update(self, file_path: Path, event_type: str):
        """Process a single file update."""
        logger.info(f"Processing file update: {file_path} ({event_type})")

        start_time = datetime.now()
        retries = 0

        while retries <= self.max_retries:
            try:
                # Process the file
                documents = self.document_processor.process_file(file_path)

                if not documents:
                    logger.warning(f"No documents extracted from {file_path}")
                    break

                # Add auto-update metadata
                for doc in documents:
                    doc.metadata.update({
                        "auto_update": True,
                        "event_type": event_type,
                        "update_timestamp": datetime.now().isoformat(),
                        "file_path": str(file_path)
                    })

                # Add to vector store
                result = self.vector_store_manager.add_documents(documents)

                if result["success"]:
                    processing_time = (datetime.now() - start_time).total_seconds()

                    self.processing_stats["files_processed"] += 1
                    self.processing_stats["last_update"] = datetime.now().isoformat()
                    self.processing_stats["total_processing_time"] += processing_time

                    logger.info(f"Successfully processed {file_path} in {processing_time:.2f}s")
                    break
                else:
                    raise Exception(f"Vector store update failed: {result.get('error')}")

            except Exception as e:
                retries += 1
                if retries <= self.max_retries:
                    wait_time = retries * 2  # Exponential backoff
                    logger.warning(f"Retry {retries}/{self.max_retries} for {file_path} in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    self.processing_stats["files_failed"] += 1
                    logger.error(f"Failed to process {file_path} after {self.max_retries} retries: {e}")
                    break

    def batch_process_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, Any]:
        """Batch process all files in a directory."""
        directory_path = Path(directory_path)
        if not directory_path.exists():
            return {"success": False, "error": f"Directory not found: {directory_path}"}

        logger.info(f"Starting batch processing of directory: {directory_path}")

        start_time = datetime.now()
        stats = {
            "files_found": 0,
            "files_processed": 0,
            "files_failed": 0,
            "documents_generated": 0,
            "processing_time": 0.0
        }

        try:
            # Find all supported files
            supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md', '.py', '.js', '.sol', '.cdc'}
            pattern = "**/*" if recursive else "*"

            files_to_process = []
            for file_path in directory_path.glob(pattern):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    files_to_process.append(file_path)

            stats["files_found"] = len(files_to_process)

            if not files_to_process:
                logger.info("No supported files found in directory")
                return {
                    "success": True,
                    "stats": stats,
                    "message": "No supported files found"
                }

            # Process each file
            for file_path in files_to_process:
                try:
                    documents = self.document_processor.process_file(file_path)

                    if documents:
                        # Add auto-update metadata
                        for doc in documents:
                            doc.metadata.update({
                                "auto_update": True,
                                "event_type": "batch_process",
                                "update_timestamp": datetime.now().isoformat(),
                                "file_path": str(file_path)
                            })

                        result = self.vector_store_manager.add_documents(documents)

                        if result["success"]:
                            stats["files_processed"] += 1
                            stats["documents_generated"] += len(documents)
                        else:
                            stats["files_failed"] += 1
                            logger.error(f"Failed to add documents from {file_path}")
                    else:
                        stats["files_failed"] += 1
                        logger.warning(f"No documents extracted from {file_path}")

                except Exception as e:
                    stats["files_failed"] += 1
                    logger.error(f"Failed to process {file_path}: {e}")

            processing_time = (datetime.now() - start_time).total_seconds()
            stats["processing_time"] = processing_time

            logger.info(f"Batch processing complete: {stats}")

            return {
                "success": True,
                "stats": stats
            }

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            stats["processing_time"] = processing_time

            logger.error(f"Batch processing failed: {e}")
            return {
                "success": False,
                "stats": stats,
                "error": str(e)
            }

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics."""
        collection_stats = self.vector_store_manager.get_collection_stats()

        return {
            "auto_update_stats": self.processing_stats.copy(),
            "collection_stats": collection_stats,
            "watch_directories": [str(d) for d in self.watch_directories],
            "running": self.running,
            "observers_count": len(self.observers),
            "debounce_seconds": self.debounce_seconds,
            "max_retries": self.max_retries
        }

    def cleanup_old_documents(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old documents from the auto-update collection."""
        logger.info(f"Starting cleanup of documents older than {days_old} days")

        try:
            # This is a simplified cleanup - in production, you'd want more sophisticated logic
            # For now, we'll just reset the collection and re-index recent files
            old_count = self.vector_store_manager.get_collection_stats().get("total_documents", 0)

            # Reset collection
            self.vector_store_manager.reset_collection()

            # Re-process recent files from watch directories
            reprocessed = 0
            cutoff_date = datetime.now() - timedelta(days=days_old)

            for directory in self.watch_directories:
                if directory.exists():
                    for file_path in directory.rglob("*"):
                        if file_path.is_file():
                            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                            if file_time > cutoff_date:
                                try:
                                    self.process_file_update(file_path, "cleanup_reprocess")
                                    reprocessed += 1
                                except Exception as e:
                                    logger.error(f"Failed to reprocess {file_path} during cleanup: {e}")

            new_count = self.vector_store_manager.get_collection_stats().get("total_documents", 0)

            return {
                "success": True,
                "old_document_count": old_count,
                "new_document_count": new_count,
                "reprocessed_files": reprocessed,
                "cleaned_documents": old_count - new_count
            }

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        vector_store_health = self.vector_store_manager.health_check()

        return {
            "auto_update_healthy": self.running,
            "watch_directories_accessible": all(d.exists() for d in self.watch_directories),
            "observers_running": len([o for o in self.observers if o.is_alive()]),
            "vector_store_health": vector_store_health,
            "processing_stats": self.processing_stats
        }