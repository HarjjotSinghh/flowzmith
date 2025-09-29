"""
API routes for IPFS contract management.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from ..models.database import get_db
from ..models.contract import GeneratedConfiguration
from ..services.llm_service import LLMService
from ..services.pinata_service import get_pinata_service, PinataError
from ..config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ipfs", tags=["IPFS Storage"])


class IPFSUploadResponse(BaseModel):
    """Response model for IPFS uploads."""
    success: bool
    ipfs_cid: Optional[str] = None
    gateway_url: Optional[str] = None
    message: str
    metadata: Optional[Dict[str, Any]] = None


class IPFSRetrievalResponse(BaseModel):
    """Response model for IPFS retrieval."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str


class IPFSStatusResponse(BaseModel):
    """Response model for IPFS service status."""
    enabled: bool
    authenticated: bool
    gateway_configured: bool
    message: str


class ContractIPFSInfo(BaseModel):
    """Model for contract IPFS information."""
    config_id: str
    ipfs_cid: Optional[str] = None
    ipfs_uploaded_at: Optional[str] = None
    gateway_url: Optional[str] = None
    ipfs_metadata: Optional[Dict[str, Any]] = None


@router.get("/status", response_model=IPFSStatusResponse)
async def get_ipfs_status():
    """Get IPFS service status and configuration."""
    settings = get_settings()
    pinata_service = get_pinata_service()
    
    if not settings.enable_ipfs_storage:
        return IPFSStatusResponse(
            enabled=False,
            authenticated=False,
            gateway_configured=bool(settings.pinata_gateway),
            message="IPFS storage is disabled in configuration"
        )
    
    if not pinata_service:
        return IPFSStatusResponse(
            enabled=True,
            authenticated=False,
            gateway_configured=bool(settings.pinata_gateway),
            message="Pinata service not initialized - check JWT configuration"
        )
    
    # Test authentication
    try:
        auth_status = await pinata_service.test_authentication()
        return IPFSStatusResponse(
            enabled=True,
            authenticated=auth_status,
            gateway_configured=bool(settings.pinata_gateway),
            message="IPFS service is operational" if auth_status else "Authentication failed"
        )
    except Exception as e:
        return IPFSStatusResponse(
            enabled=True,
            authenticated=False,
            gateway_configured=bool(settings.pinata_gateway),
            message=f"Error testing authentication: {str(e)}"
        )


@router.get("/contract/{config_id}", response_model=IPFSRetrievalResponse)
async def get_contract_from_ipfs(
    config_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve contract from IPFS by configuration ID."""
    try:
        # Get the configuration record
        config = db.query(GeneratedConfiguration).filter(
            GeneratedConfiguration.id == config_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuration not found"
            )
        
        if not config.ipfs_cid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract not stored on IPFS"
            )
        
        # Initialize LLM service to access IPFS methods
        llm_service = LLMService(db)
        
        # Retrieve from IPFS
        ipfs_data = await llm_service.retrieve_contract_from_ipfs(config.ipfs_cid)
        
        if not ipfs_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve contract from IPFS"
            )
        
        return IPFSRetrievalResponse(
            success=True,
            data=ipfs_data,
            message="Contract retrieved successfully from IPFS"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving contract from IPFS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/contract/{config_id}/upload", response_model=IPFSUploadResponse)
async def upload_contract_to_ipfs(
    config_id: str,
    db: Session = Depends(get_db)
):
    """Upload an existing contract to IPFS."""
    try:
        # Get the configuration record
        config = db.query(GeneratedConfiguration).filter(
            GeneratedConfiguration.id == config_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuration not found"
            )
        
        if config.ipfs_cid:
            # Already uploaded, return existing info
            settings = get_settings()
            gateway_url = f"https://{settings.pinata_gateway}/ipfs/{config.ipfs_cid}" if settings.pinata_gateway else None
            
            return IPFSUploadResponse(
                success=True,
                ipfs_cid=config.ipfs_cid,
                gateway_url=gateway_url,
                message="Contract already stored on IPFS",
                metadata=config.ipfs_metadata
            )
        
        # Initialize LLM service
        llm_service = LLMService(db)
        
        if not llm_service.pinata_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="IPFS storage service not available"
            )
        
        # Get the submission for metadata
        submission = config.contract_submission
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract submission not found"
            )
        
        # Upload to IPFS
        ipfs_result = await llm_service._upload_contract_to_ipfs(config, submission)
        
        if not ipfs_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload contract to IPFS"
            )
        
        # Update the configuration with IPFS info
        config.ipfs_cid = ipfs_result.get("ipfs_cid")
        config.ipfs_pin_id = ipfs_result.get("pin_id")
        config.ipfs_uploaded_at = datetime.utcnow()
        config.ipfs_metadata = ipfs_result.get("pinata_metadata")
        
        db.commit()
        
        return IPFSUploadResponse(
            success=True,
            ipfs_cid=config.ipfs_cid,
            gateway_url=ipfs_result.get("gateway_url"),
            message="Contract uploaded to IPFS successfully",
            metadata=config.ipfs_metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading contract to IPFS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/contracts", response_model=List[ContractIPFSInfo])
async def list_contracts_on_ipfs(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List all contracts stored on IPFS."""
    try:
        settings = get_settings()
        
        # Query configurations with IPFS CIDs
        configs = db.query(GeneratedConfiguration).filter(
            GeneratedConfiguration.ipfs_cid.isnot(None)
        ).offset(offset).limit(limit).all()
        
        result = []
        for config in configs:
            gateway_url = None
            if settings.pinata_gateway and config.ipfs_cid:
                gateway_url = f"https://{settings.pinata_gateway}/ipfs/{config.ipfs_cid}"
            
            result.append(ContractIPFSInfo(
                config_id=str(config.id),
                ipfs_cid=config.ipfs_cid,
                ipfs_uploaded_at=config.ipfs_uploaded_at.isoformat() if config.ipfs_uploaded_at else None,
                gateway_url=gateway_url,
                ipfs_metadata=config.ipfs_metadata
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing contracts on IPFS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/contract/{config_id}/unpin", response_model=Dict[str, Any])
async def unpin_contract_from_ipfs(
    config_id: str,
    db: Session = Depends(get_db)
):
    """Unpin a contract from IPFS (remove from Pinata)."""
    try:
        # Get the configuration record
        config = db.query(GeneratedConfiguration).filter(
            GeneratedConfiguration.id == config_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuration not found"
            )
        
        if not config.ipfs_cid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract not stored on IPFS"
            )
        
        # Get Pinata service
        pinata_service = get_pinata_service()
        if not pinata_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="IPFS storage service not available"
            )
        
        # Unpin from Pinata
        success = await pinata_service.unpin_from_ipfs(config.ipfs_cid)
        
        if success:
            # Clear IPFS fields from database
            config.ipfs_cid = None
            config.ipfs_pin_id = None
            config.ipfs_uploaded_at = None
            config.ipfs_metadata = None
            db.commit()
            
            return {
                "success": True,
                "message": "Contract unpinned from IPFS successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to unpin contract from IPFS"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unpinning contract from IPFS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/contract/{config_id}/sync", response_model=Dict[str, Any])
async def sync_contract_metadata(
    config_id: str,
    db: Session = Depends(get_db)
):
    """Sync contract metadata from IPFS."""
    try:
        # Get the configuration record
        config = db.query(GeneratedConfiguration).filter(
            GeneratedConfiguration.id == config_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuration not found"
            )
        
        if not config.ipfs_cid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract not stored on IPFS"
            )
        
        # Initialize LLM service
        llm_service = LLMService(db)
        
        # Sync metadata
        success = await llm_service.sync_ipfs_metadata(config)
        
        return {
            "success": success,
            "message": "Metadata synced successfully" if success else "Failed to sync metadata",
            "metadata": config.ipfs_metadata if success else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing contract metadata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
