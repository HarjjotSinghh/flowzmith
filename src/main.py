"""
Main application entry point for Smart Contract LLM Builder.
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.api import router, websocket_router
from src.api.middleware import (
    AuthenticationMiddleware,
    RateLimitMiddleware,
    ValidationMiddleware,
    CORSMiddleware as CustomCORSMiddleware,
    SecurityHeadersMiddleware,
    LoggingMiddleware
)
from src.api.exceptions import (
    error_handler,
    smart_contract_exception_handler,
    http_exception_handler,
    request_validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler,
    SmartContractError
)
from src.config import get_settings
from src.models.database import create_tables, check_database_connection, get_db
from src.models import User, ContractSubmission, DeploymentLog, DocumentationKnowledgeBase
from src.config import get_settings
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('smart_contract_llm.log')
    ]
)

logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting Smart Contract LLM Builder application...")

    # Initialize database
    try:
        if not check_database_connection():
            logger.error("Failed to connect to database")
            raise Exception("Database connection failed")

        # create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    # Create necessary directories
    os.makedirs(settings.flow_projects_path, exist_ok=True)
    os.makedirs(settings.vector_db_path, exist_ok=True)
    os.makedirs(settings.log_path, exist_ok=True)

    logger.info("Application started successfully")
    yield

    logger.info("Shutting down Smart Contract LLM Builder application...")


# Create FastAPI application
app = FastAPI(
    title="Smart Contract LLM Builder",
    description="AI-powered smart contract generation and deployment platform for Flow blockchain",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(CustomCORSMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ValidationMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthenticationMiddleware)

# Add exception handlers
app.add_exception_handler(SmartContractError, smart_contract_exception_handler)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Include WebSocket routes
app.include_router(websocket_router)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard page."""
    # Get dashboard statistics
    try:
        total_contracts = db.query(ContractSubmission).count()
        successful_deployments = db.query(DeploymentLog).filter(DeploymentLog.status == 'SUCCESS').count()
        pending_submissions = db.query(ContractSubmission).filter(ContractSubmission.status == 'PENDING').count()
        total_docs = db.query(DocumentationKnowledgeBase).count()

        # Get recent submissions (convert to dict to avoid template serialization issues)
        recent_submissions = []
        for submission in db.query(ContractSubmission).order_by(ContractSubmission.created_at.desc()).limit(10).all():
            recent_submissions.append({
                'id': str(submission.id),
                'contract_name': submission.contract_name,
                'status': submission.status.value if hasattr(submission.status, 'value') else str(submission.status),
                'created_at': submission.created_at.isoformat() if submission.created_at else None
            })
    except Exception as e:
        logger.error(f"Database query error: {e}")
        # Use default values if database fails
        total_contracts = 0
        successful_deployments = 0
        pending_submissions = 0
        total_docs = 0
        recent_submissions = []

    # Mock recent activity data
    recent_activity = [
        {
            "type": "submission",
            "title": "New contract submitted",
            "description": "NFT Marketplace Contract",
            "timestamp": "2 minutes ago"
        },
        {
            "type": "deployment",
            "title": "Deployment completed",
            "description": "Token Contract on testnet",
            "timestamp": "15 minutes ago"
        }
    ]

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_contracts": total_contracts,
        "successful_deployments": successful_deployments,
        "pending_submissions": pending_submissions,
        "total_docs": total_docs,
        "recent_submissions": recent_submissions,
        "recent_activity": recent_activity
    })


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        db_healthy = check_database_connection()

        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "timestamp": "2025-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "error",
                "error": str(e)
            }
        )


# Frontend pages
@app.get("/submit", response_class=HTMLResponse)
async def submit_page(request: Request, db: Session = Depends(get_db)):
    """Submit contract page."""
    # Get available submissions for reference
    try:
        available_submissions = []
        for submission in db.query(ContractSubmission).filter(ContractSubmission.status == 'COMPLETED').limit(20).all():
            available_submissions.append({
                'id': str(submission.id),
                'contract_name': submission.contract_name,
                'status': submission.status.value if hasattr(submission.status, 'value') else str(submission.status),
                'created_at': submission.created_at.isoformat() if submission.created_at else None
            })
    except Exception as e:
        logger.error(f"Database query error in submit page: {e}")
        available_submissions = []

    return templates.TemplateResponse("submit.html", {
        "request": request,
        "available_submissions": available_submissions
    })


@app.get("/deployments", response_class=HTMLResponse)
async def deployments_page(request: Request, db: Session = Depends(get_db)):
    """Deployments management page."""
    try:
        deployments = db.query(DeploymentLog).order_by(DeploymentLog.created_at.desc()).limit(50).all()

        # Calculate statistics
        total_deployments = db.query(DeploymentLog).count()
        successful_deployments = db.query(DeploymentLog).filter(DeploymentLog.status == 'SUCCESS').count()
        failed_deployments = db.query(DeploymentLog).filter(DeploymentLog.status == 'FAILED').count()
        pending_deployments = db.query(DeploymentLog).filter(DeploymentLog.status == 'PENDING').count()

        # Get completed submissions for new deployment dropdown
        available_submissions = []
        for submission in db.query(ContractSubmission).filter(ContractSubmission.status == 'COMPLETED').all():
            available_submissions.append({
                'id': str(submission.id),
                'contract_name': submission.contract_name,
                'status': submission.status.value if hasattr(submission.status, 'value') else str(submission.status),
                'created_at': submission.created_at.isoformat() if submission.created_at else None
            })

        # Convert deployments to dict for JSON serialization
        deployments_list = []
        for d in deployments:
            deployments_list.append({
                'id': str(d.id),
                'contract_name': d.contract_submission.contract_name if d.contract_submission else 'Unknown',
                'network': d.network,
                'status': d.status.value if hasattr(d.status, 'value') else str(d.status),
                'created_at': d.created_at.isoformat() if d.created_at else None,
                'execution_time_ms': d.execution_time_ms,
                'submission_id': str(d.submission_id),
                'transaction_hash': d.transaction_hash,
                'error_message': d.error_message
            })

    except Exception as e:
        logger.error(f"Database query error in deployments page: {e}")
        deployments = []
        deployments_list = []
        total_deployments = 0
        successful_deployments = 0
        failed_deployments = 0
        pending_deployments = 0
        available_submissions = []

    return templates.TemplateResponse("deployments.html", {
        "request": request,
        "deployments": deployments,
        "deployments_json": json.dumps(deployments_list, default=str),
        "total_deployments": total_deployments,
        "successful_deployments": successful_deployments,
        "failed_deployments": failed_deployments,
        "pending_deployments": pending_deployments,
        "available_submissions": available_submissions
    })


@app.get("/docs", response_class=HTMLResponse)
async def docs_page(request: Request, db: Session = Depends(get_db)):
    """Documentation page."""
    query = request.query_params.get("q", "")
    results = []

    if query:
        # Simple text search for now (can be enhanced with vector search)
        search_query = f"%{query}%"
        results = db.query(DocumentationKnowledgeBase).filter(
            DocumentationKnowledgeBase.title.ilike(search_query) |
            DocumentationKnowledgeBase.content.ilike(search_query)
        ).limit(50).all()

    return templates.TemplateResponse("docs.html", {
        "request": request,
        "query": query,
        "results": results
    })


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page."""
    return templates.TemplateResponse("profile.html", {
        "request": request
    })


# API endpoint for dashboard stats
@app.get("/api/dashboard/stats")
async def dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    return {
        "total_contracts": db.query(ContractSubmission).count(),
        "successful_deployments": db.query(DeploymentLog).filter(DeploymentLog.status == 'SUCCESS').count(),
        "pending_submissions": db.query(ContractSubmission).filter(ContractSubmission.status == 'PENDING').count(),
        "total_docs": db.query(DocumentationKnowledgeBase).count()
    }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint."""
    return {
        "name": "Smart Contract LLM Builder",
        "version": "1.0.0",
        "description": "AI-powered smart contract generation and deployment platform",
        "features": [
            "Multi-modal input processing (CDC files, Solidity files, natural language)",
            "AI-powered contract generation using OpenAI/Groq",
            "Flow blockchain deployment and management",
            "Real-time deployment monitoring",
            "Learning feedback loops for continuous improvement",
            "Vector-based documentation search",
            "User data privacy controls"
        ],
        "endpoints": {
            "contracts": "/api/v1/contracts",
            "deployments": "/api/v1/deployments",
            "documentation": "/api/v1/documentation",
            "users": "/api/v1/users",
            "statistics": "/api/v1/statistics",
            "websocket": "/api/v1/ws"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )