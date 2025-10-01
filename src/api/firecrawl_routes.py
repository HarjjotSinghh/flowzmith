"""
Firecrawl API endpoints.

Provides REST API endpoints for web crawling and scraping operations
using Firecrawl service integration.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl, Field

from src.models.database import get_db
from src.services.documentation_service import DocumentationService
from src.services.firecrawl_service import FirecrawlService
from src.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/firecrawl", tags=["firecrawl"])
settings = get_settings()


# Pydantic models for request/response
class ScrapeRequest(BaseModel):
    """Request model for scraping a single URL."""
    url: HttpUrl
    format: str = Field(default="markdown", description="Output format: markdown, html, or text")
    only_main_content: bool = Field(default=True, description="Extract only main content")
    include_tags: Optional[List[str]] = Field(default=None, description="HTML tags to include")
    exclude_tags: Optional[List[str]] = Field(default=None, description="HTML tags to exclude")
    timeout: int = Field(default=30000, description="Timeout in milliseconds")


class CrawlRequest(BaseModel):
    """Request model for crawling a website."""
    url: HttpUrl
    max_pages: int = Field(default=10, description="Maximum number of pages to crawl")
    include_paths: Optional[List[str]] = Field(default=None, description="URL patterns to include")
    exclude_paths: Optional[List[str]] = Field(default=None, description="URL patterns to exclude")
    format: str = Field(default="markdown", description="Output format: markdown, html, or text")
    only_main_content: bool = Field(default=True, description="Extract only main content")
    timeout: int = Field(default=30000, description="Timeout in milliseconds")


class IndexContentRequest(BaseModel):
    """Request model for indexing scraped content."""
    url: HttpUrl
    title: str
    content: str
    source: str = Field(default="CUSTOM_DOCUMENTATION")
    content_type: Optional[str] = Field(default=None, description="Content type classification")


class CrawlResponse(BaseModel):
    """Response model for crawl operations."""
    success: bool
    message: Optional[str] = None
    crawl_id: Optional[str] = None
    pages_found: Optional[int] = None
    error: Optional[str] = None


class ScrapeResponse(BaseModel):
    """Response model for scrape operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    error: Optional[str] = None


class IndexResponse(BaseModel):
    """Response model for indexing operations."""
    success: bool
    document_id: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


@router.get("/health")
async def health_check():
    """Check Firecrawl service health."""
    try:
        firecrawl_service = FirecrawlService()
        is_available = firecrawl_service.is_available()
        
        return JSONResponse(
            status_code=200 if is_available else 503,
            content={
                "status": "healthy" if is_available else "unavailable",
                "service": "firecrawl",
                "available": is_available
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "service": "firecrawl",
                "available": False,
                "error": str(e)
            }
        )


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_url(
    request: ScrapeRequest,
    db: Session = Depends(get_db)
):
    """Scrape a single URL and return the content."""
    try:
        firecrawl_service = FirecrawlService()
        
        if not firecrawl_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Firecrawl service is not available"
            )

        # Prepare scrape options
        scrape_options = {
            "formats": [request.format],
            "only_main_content": request.only_main_content,
            "timeout": request.timeout
        }

        if request.include_tags:
            scrape_options["include_tags"] = request.include_tags
        if request.exclude_tags:
            scrape_options["exclude_tags"] = request.exclude_tags

        # Perform scrape
        result = firecrawl_service.scrape_url(str(request.url), **scrape_options)
        
        if result.get("success", False):
            return ScrapeResponse(
                success=True,
                data=result.get("data", {}),
                url=str(request.url)
            )
        else:
            return ScrapeResponse(
                success=False,
                error="Failed to scrape URL",
                url=str(request.url)
            )

    except Exception as e:
        logger.error(f"Error scraping URL {request.url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl", response_model=CrawlResponse)
async def crawl_website(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Crawl a website and return crawl information."""
    try:
        firecrawl_service = FirecrawlService()
        
        if not firecrawl_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Firecrawl service is not available"
            )

        # Prepare crawl options
        crawl_options = {
            "limit": request.max_pages,
            "scrape_options": {
                "formats": [request.format],
                "only_main_content": request.only_main_content,
                "timeout": request.timeout
            }
        }

        if request.include_paths:
            crawl_options["include_paths"] = request.include_paths
        if request.exclude_paths:
            crawl_options["exclude_paths"] = request.exclude_paths

        # Start crawl
        result = firecrawl_service.crawl_url(str(request.url), **crawl_options)
        
        if result.get("success", False):
            return CrawlResponse(
                success=True,
                message="Crawl started successfully",
                crawl_id=result.get("id"),
                pages_found=len(result.get("data", []))
            )
        else:
            return CrawlResponse(
                success=False,
                error="Failed to start crawl"
            )

    except Exception as e:
        logger.error(f"Error crawling website {request.url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crawl/{crawl_id}/status")
async def get_crawl_status(crawl_id: str):
    """Get the status of a crawl job."""
    try:
        firecrawl_service = FirecrawlService()
        
        if not firecrawl_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Firecrawl service is not available"
            )

        result = firecrawl_service.get_crawl_status(crawl_id)
        
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error getting crawl status for {crawl_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/crawl/cadence", response_model=Dict[str, Any])
async def crawl_cadence_documentation(
    force_refresh: bool = False,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Crawl and index Cadence documentation."""
    try:
        documentation_service = DocumentationService(db)
        
        # Start crawl and indexing
        result = documentation_service.crawl_and_index_cadence_docs(force_refresh=force_refresh)
        
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error crawling Cadence documentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index", response_model=IndexResponse)
async def index_content(
    request: IndexContentRequest,
    db: Session = Depends(get_db)
):
    """Index scraped content into the knowledge base."""
    try:
        documentation_service = DocumentationService(db)
        
        # Index the content
        doc_entry = documentation_service.index_scraped_content(
            url=str(request.url),
            title=request.title,
            content=request.content,
            source=request.source
        )
        
        return IndexResponse(
            success=True,
            document_id=doc_entry.id,
            message=f"Content indexed successfully: {request.title}"
        )

    except Exception as e:
        logger.error(f"Error indexing content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape-and-index", response_model=IndexResponse)
async def scrape_and_index(
    url: HttpUrl,
    title: Optional[str] = None,
    source: str = "CUSTOM_DOCUMENTATION",
    db: Session = Depends(get_db)
):
    """Scrape a URL and immediately index the content."""
    try:
        documentation_service = DocumentationService(db)
        
        # Scrape the URL
        scrape_result = documentation_service.scrape_single_page(str(url))
        
        if not scrape_result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=f"Failed to scrape URL: {scrape_result.get('error', 'Unknown error')}"
            )

        # Extract content and metadata
        data = scrape_result.get("data", {})
        content = data.get("markdown", data.get("html", ""))
        extracted_title = data.get("metadata", {}).get("title", "")
        
        # Use provided title or extracted title
        final_title = title or extracted_title or str(url).split("/")[-1]
        
        if not content or len(content.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Insufficient content found on the page"
            )

        # Index the content
        doc_entry = documentation_service.index_scraped_content(
            url=str(url),
            title=final_title,
            content=content,
            source=source
        )
        
        return IndexResponse(
            success=True,
            document_id=doc_entry.id,
            message=f"Content scraped and indexed successfully: {final_title}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping and indexing {url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documentation/stats")
async def get_documentation_stats(db: Session = Depends(get_db)):
    """Get statistics about indexed documentation."""
    try:
        documentation_service = DocumentationService(db)
        stats = documentation_service.get_documentation_stats()
        
        return JSONResponse(content=stats)

    except Exception as e:
        logger.error(f"Error getting documentation stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))