"""
Knowledge Base API endpoints.

Provides REST API endpoints for knowledge base operations including
document ingestion, search, and management.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.config import get_settings
from knowledge_base import KnowledgeBaseManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])
settings = get_settings()

# Global knowledge base manager instance
kb_manager = None


def get_kb_manager() -> KnowledgeBaseManager:
    """Get or create knowledge base manager instance."""
    global kb_manager
    if kb_manager is None:
        try:
            # Initialize knowledge base manager
            kb_manager = KnowledgeBaseManager(
                knowledge_base_path="./knowledge_base",
                collection_name="smart_contracts",
                embedding_model="text-embedding-ada-002",
                chunk_size=1000,
                chunk_overlap=200,
                watch_directories=["./docs", "./contracts"],
                auto_update_enabled=True,
                debounce_seconds=10
            )
            logger.info("Knowledge Base Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Knowledge Base Manager: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize knowledge base: {str(e)}")
    return kb_manager


@router.post("/documents")
async def add_documents(
    source: str = Form(...),
    source_type: str = Form(...),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Add documents to the knowledge base."""
    try:
        kb = get_kb_manager()

        # Parse metadata if provided
        doc_metadata = {}
        if metadata:
            import json
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")

        # Add documents
        result = kb.add_documents(
            source=source,
            source_type=source_type,
            metadata=doc_metadata
        )

        if result["success"]:
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to add documents"))

    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload and add documents to the knowledge base."""
    try:
        kb = get_kb_manager()

        # Parse metadata if provided
        doc_metadata = {}
        if metadata:
            import json
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")

        # Create temporary directory for uploads
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        uploaded_files = []

        try:
            # Save uploaded files
            for file in files:
                file_path = Path(temp_dir) / file.filename
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                uploaded_files.append(str(file_path))

            # Add documents
            result = kb.add_documents(
                source=uploaded_files,
                source_type="file",
                metadata=doc_metadata
            )

            return JSONResponse(content=result)

        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_knowledge_base(
    query: str,
    top_k: int = 5,
    filters: Optional[str] = None,
    similarity_threshold: float = 0.7,
    search_type: str = "semantic",
    include_metadata: bool = True,
    db: Session = Depends(get_db)
):
    """Search the knowledge base."""
    try:
        kb = get_kb_manager()

        # Parse filters if provided
        search_filters = {}
        if filters:
            import json
            try:
                search_filters = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid filters JSON")

        # Perform search
        result = kb.search(
            query=query,
            top_k=top_k,
            filters=search_filters,
            similarity_threshold=similarity_threshold,
            search_type=search_type,
            include_metadata=include_metadata
        )

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/suggestions")
async def get_search_suggestions(
    query: str,
    max_suggestions: int = 5,
    db: Session = Depends(get_db)
):
    """Get search query suggestions."""
    try:
        kb = get_kb_manager()
        suggestions = kb.suggest_related_queries(query, max_suggestions)
        return JSONResponse(content={
            "success": True,
            "query": query,
            "suggestions": suggestions
        })

    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-update/start")
async def start_auto_update(db: Session = Depends(get_db)):
    """Start the auto-updating file watcher."""
    try:
        kb = get_kb_manager()
        result = kb.start_auto_update()
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error starting auto-update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-update/stop")
async def stop_auto_update(db: Session = Depends(get_db)):
    """Stop the auto-updating file watcher."""
    try:
        kb = get_kb_manager()
        result = kb.stop_auto_update()
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error stopping auto-update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_knowledge_base_stats(db: Session = Depends(get_db)):
    """Get knowledge base statistics."""
    try:
        kb = get_kb_manager()
        stats = kb.get_statistics()
        return JSONResponse(content={
            "success": True,
            "statistics": stats
        })

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def knowledge_base_health_check(db: Session = Depends(get_db)):
    """Perform health check of the knowledge base."""
    try:
        kb = get_kb_manager()
        health = kb.health_check()
        return JSONResponse(content={
            "success": True,
            "health": health
        })

    except Exception as e:
        logger.error(f"Error performing health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_knowledge_base(
    export_path: str = "./knowledge_base_export.json",
    db: Session = Depends(get_db)
):
    """Export the knowledge base to a file."""
    try:
        kb = get_kb_manager()
        result = kb.export_knowledge_base(export_path)
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error exporting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_knowledge_base(
    import_path: str = Form(...),
    db: Session = Depends(get_db)
):
    """Import knowledge base from a file."""
    try:
        kb = get_kb_manager()
        result = kb.import_knowledge_base(import_path)
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error importing knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_old_documents(
    days_old: int = 30,
    db: Session = Depends(get_db)
):
    """Clean up old documents from the knowledge base."""
    try:
        kb = get_kb_manager()
        result = kb.cleanup_old_documents(days_old)
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error cleaning up documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_knowledge_base(db: Session = Depends(get_db)):
    """Reset the knowledge base (delete all data)."""
    try:
        kb = get_kb_manager()
        result = kb.reset_knowledge_base()
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error resetting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections")
async def get_collections_info(db: Session = Depends(get_db)):
    """Get information about available collections."""
    try:
        kb = get_kb_manager()
        result = kb.get_collection_info()
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error getting collections info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auto-update/status")
async def get_auto_update_status(db: Session = Depends(get_db)):
    """Get auto-update status and statistics."""
    try:
        kb = get_kb_manager()
        if kb.knowledge_base_updater:
            stats = kb.knowledge_base_updater.get_processing_stats()
            return JSONResponse(content={
                "success": True,
                "auto_update_enabled": True,
                "stats": stats
            })
        else:
            return JSONResponse(content={
                "success": True,
                "auto_update_enabled": False,
                "message": "Auto-updater not initialized"
            })

    except Exception as e:
        logger.error(f"Error getting auto-update status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-process")
async def batch_process_directory(
    directory_path: str = Form(...),
    recursive: bool = Form(True),
    metadata: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Batch process all documents in a directory."""
    try:
        kb = get_kb_manager()

        # Parse metadata if provided
        doc_metadata = {}
        if metadata:
            import json
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")

        if kb.knowledge_base_updater:
            result = kb.knowledge_base_updater.batch_process_directory(
                directory_path=directory_path,
                recursive=recursive
            )
            return JSONResponse(content=result)
        else:
            return JSONResponse(content={
                "success": False,
                "error": "Auto-updater not initialized"
            })

    except Exception as e:
        logger.error(f"Error batch processing directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))