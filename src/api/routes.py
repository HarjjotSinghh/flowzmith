"""
API routes for Smart Contract LLM Builder.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid

from ..models.database import get_db
from ..services import (
    LLMService,
    FlowService,
    DocumentationService,
    UserService,
    LearningService,
    DataControlService
)
from ..schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    ContractSubmissionCreate,
    ContractSubmissionResponse,
    GeneratedConfigurationResponse,
    DeploymentLogResponse,
    TransactionProposalCreate,
    TransactionProposalResponse,
    DocumentationSearchRequest,
    DocumentationResponse,
    LearningFeedbackResponse,
    DataControlUpdate,
    DataControlResponse,
    ExportRequest,
    ExportResponse,
    DeleteDataRequest,
    DeleteDataResponse,
    ContractGenerationRequest,
    ContractGenerationResponse,
    DeploymentRequest,
    DeploymentResponse,
    TransactionApprovalRequest,
    StatisticsResponse,
    HealthResponse,
    ErrorResponse
)

# Create main router
router = APIRouter()

# Health check endpoint
@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Check database connection
        from ..models.database import check_database_connection
        db_connected = check_database_connection()

        # Check LLM providers
        from ..config import get_settings
        settings = get_settings()
        llm_providers = []
        if settings.openai_api_key:
            llm_providers.append("OpenAI")
        if settings.groq_api_key:
            llm_providers.append("Groq")

        # Check Flow CLI
        flow_cli_available = False
        try:
            import subprocess
            result = subprocess.run(["flow", "version"], capture_output=True, text=True)
            flow_cli_available = result.returncode == 0
        except:
            pass

        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            database_connected=db_connected,
            llm_providers=llm_providers,
            flow_cli_available=flow_cli_available
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User routes
@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    try:
        user_service = UserService(db)
        user = user_service.create_user(
            email=user_data.email,
            password=user_data.password,
            persona_type=user_data.persona_type,
            full_name=user_data.full_name,
            organization=user_data.organization
        )
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/login")
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user."""
    try:
        user_service = UserService(db)
        user = user_service.authenticate_user(login_data.email, login_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"message": "Login successful", "user_id": str(user.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/me", response_model=UserResponse)
async def get_current_user(user_id: str, db: Session = Depends(get_db)):
    """Get current user profile."""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.from_orm(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/me", response_model=UserResponse)
async def update_user_profile(
    user_id: str,
    updates: dict,
    db: Session = Depends(get_db)
):
    """Update user profile."""
    try:
        user_service = UserService(db)
        user = user_service.update_user_profile(user_id, updates)
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Contract submission routes
@router.post("/contracts", response_model=ContractGenerationResponse)
async def generate_contract(
    request: ContractGenerationRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Generate contract from user input."""
    try:
        # Create submission
        user_service = UserService(db)
        llm_service = LLMService(db)
        flow_service = FlowService(db)

        # Create contract submission
        from ..models import ContractSubmission
        submission = ContractSubmission(
            user_id=user_id,
            input_type=request.input_type,
            content=request.content,
            pre_conditions=request.pre_conditions,
            post_conditions=request.post_conditions
        )
        db.add(submission)
        db.commit()

        # Generate contract and configuration
        generated_config = await llm_service.generate_contract_from_submission(submission)

        # Validate configuration
        await llm_service.validate_configuration(generated_config)

        # Deploy if requested
        deployment_logs = []
        if request.network != "emulator":
            deployment_log = await flow_service.deploy_contract(
                generated_config,
                network=flow_service.FlowNetwork(request.network)
            )
            deployment_logs.append(DeploymentLogResponse.from_orm(deployment_log))

        return ContractGenerationResponse(
            submission_id=submission.id,
            config_id=generated_config.id,
            generated_contract_code=generated_config.generated_contract_code,
            config_content=generated_config.config_content,
            validation_status=generated_config.validation_status,
            deployment_logs=deployment_logs
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/submit")
async def submit_contract(
    contract_data: dict,
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """Submit contract data for processing."""
    try:
        # Create submission from contract data
        from ..models import ContractSubmission, InputType, SubmissionStatus
        import uuid

        # Map input method to InputType enum
        input_type_map = {
            "natural_language": InputType.NATURAL_LANGUAGE,
            "cadence_file": InputType.CDC_FILE,
            "solidity_file": InputType.SOL_FILE,
            "direct_code": InputType.MIXED,
            "template": InputType.MIXED
        }

        input_method = contract_data.get("input_method", "direct_code")
        input_type = input_type_map.get(input_method, InputType.MIXED)

        # Convert string user_id to UUID if provided, otherwise create a default user
        if user_id:
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                user_uuid = uuid.uuid4()  # Default user if invalid
        else:
            user_uuid = uuid.uuid4()  # Default user

        submission = ContractSubmission(
            user_id=user_uuid,
            input_type=input_type,
            content=contract_data.get("content", ""),
            pre_conditions={
                "contract_name": contract_data.get("contract_name", "Unnamed Contract"),
                "contract_type": contract_data.get("contract_type", "Custom"),
                "description": contract_data.get("description", ""),
                "network": contract_data.get("network", "testnet"),
                "metadata": contract_data.get("metadata", {})
            },
            status=SubmissionStatus.PENDING
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        return {
            "submission_id": str(submission.id),
            "status": "success",
            "message": "Contract submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contracts/file")
async def upload_contract_file(
    file: UploadFile = File(...),
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """Upload contract file for processing."""
    try:
        if not file.filename.endswith(('.cdc', '.sol')):
            raise HTTPException(status_code=400, detail="Only .cdc and .sol files are supported")

        content = await file.read()
        content_str = content.decode('utf-8')

        # Determine input type
        from ..models import InputType, SubmissionStatus
        input_type = InputType.CDC_FILE if file.filename.endswith('.cdc') else InputType.SOL_FILE

        # Convert string user_id to UUID if provided, otherwise create a default user
        if user_id:
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                user_uuid = uuid.uuid4()  # Default user if invalid
        else:
            user_uuid = uuid.uuid4()  # Default user

        # Create submission
        from ..models import ContractSubmission
        submission = ContractSubmission(
            user_id=user_uuid,
            input_type=input_type,
            content=content_str,
            status=SubmissionStatus.PENDING
        )
        db.add(submission)
        db.commit()

        return {"message": "File uploaded successfully", "submission_id": str(submission.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Deployment routes
@router.post("/deployments", response_model=DeploymentResponse)
async def deploy_contract(
    request: DeploymentRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Deploy a contract."""
    try:
        flow_service = FlowService(db)

        # Get the configuration
        from ..models import GeneratedConfiguration
        config = db.query(GeneratedConfiguration).filter(
            GeneratedConfiguration.id == request.config_id
        ).first()

        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")

        # Check ownership
        if str(config.contract_submission.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Deploy contract
        deployment_log = await flow_service.deploy_contract(
            config,
            network=flow_service.FlowNetwork(request.network)
        )

        return DeploymentResponse.from_orm(deployment_log)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deployments/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(deployment_id: str, db: Session = Depends(get_db)):
    """Get deployment details."""
    try:
        from ..models import DeploymentLog
        deployment = db.query(DeploymentLog).filter(
            DeploymentLog.id == deployment_id
        ).first()

        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        return DeploymentResponse.from_orm(deployment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Transaction routes
@router.post("/transactions/proposals", response_model=TransactionProposalResponse)
async def create_transaction_proposal(
    request: TransactionProposalCreate,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Create a transaction proposal."""
    try:
        flow_service = FlowService(db)

        # Get the configuration
        from ..models import GeneratedConfiguration
        config = db.query(GeneratedConfiguration).filter(
            GeneratedConfiguration.id == request.config_id
        ).first()

        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")

        # Check ownership
        if str(config.contract_submission.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Create transaction proposal
        proposal = await flow_service.create_transaction_proposal(
            config,
            request.transaction_type,
            request.transaction_data
        )

        return TransactionProposalResponse.from_orm(proposal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transactions/{proposal_id}/approve")
async def approve_transaction(
    proposal_id: str,
    request: TransactionApprovalRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Approve or reject a transaction proposal."""
    try:
        from ..models import TransactionProposal
        proposal = db.query(TransactionProposal).filter(
            TransactionProposal.id == proposal_id
        ).first()

        if not proposal:
            raise HTTPException(status_code=404, detail="Transaction proposal not found")

        # Check ownership
        if str(proposal.generated_configuration.contract_submission.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update approval status
        if request.approved:
            proposal.user_approval_status = "APPROVED"
            proposal.signed_transaction = request.signature
        else:
            proposal.user_approval_status = "REJECTED"

        proposal.responded_at = datetime.utcnow()
        db.commit()

        return {"message": f"Transaction {request.approved and 'approved' or 'rejected'}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Documentation routes
@router.post("/documentation/search", response_model=List[DocumentationResponse])
async def search_documentation(
    request: DocumentationSearchRequest,
    db: Session = Depends(get_db)
):
    """Search documentation."""
    try:
        doc_service = DocumentationService(db)

        if request.use_semantic_search:
            # Use semantic search
            results = doc_service.semantic_search(request.query, request.limit)
            docs = [doc for doc, _ in results]
        else:
            # Use traditional search
            docs = doc_service.search_documentation(
                request.query,
                request.content_type,
                request.limit
            )

        return [DocumentationResponse.from_orm(doc) for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documentation/stats")
async def get_documentation_stats(db: Session = Depends(get_db)):
    """Get documentation statistics."""
    try:
        doc_service = DocumentationService(db)
        stats = doc_service.get_documentation_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Learning routes
@router.get("/learning/insights", response_model=List[LearningFeedbackResponse])
async def get_learning_insights(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get learning insights."""
    try:
        learning_service = LearningService(db)
        insights = learning_service.get_learning_insights(limit)
        return [LearningFeedbackResponse.from_orm(entry) for entry in insights]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learning/stats")
async def get_learning_stats(db: Session = Depends(get_db)):
    """Get learning statistics."""
    try:
        learning_service = LearningService(db)
        stats = learning_service.get_pattern_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Data control routes
@router.get("/users/me/data-control", response_model=DataControlResponse)
async def get_data_control_settings(user_id: str, db: Session = Depends(get_db)):
    """Get user data control settings."""
    try:
        data_control_service = DataControlService(db)
        settings = data_control_service.get_user_data_control(user_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Data control settings not found")
        return DataControlResponse.from_orm(settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/me/data-control", response_model=DataControlResponse)
async def update_data_control_settings(
    user_id: str,
    request: DataControlUpdate,
    db: Session = Depends(get_db)
):
    """Update user data control settings."""
    try:
        data_control_service = DataControlService(db)
        settings = data_control_service.update_data_control_settings(
            user_id,
            request.dict(exclude_unset=True)
        )
        return DataControlResponse.from_orm(settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/me/export", response_model=ExportResponse)
async def export_user_data(
    user_id: str,
    request: ExportRequest,
    db: Session = Depends(get_db)
):
    """Export user data."""
    try:
        data_control_service = DataControlService(db)
        export_data = data_control_service.export_user_data(user_id, request.format_type)
        return ExportResponse(
            format=export_data["format"],
            data=export_data["data"],
            exported_at=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/me/data", response_model=DeleteDataResponse)
async def delete_user_data(
    user_id: str,
    request: DeleteDataRequest,
    db: Session = Depends(get_db)
):
    """Delete user data."""
    try:
        data_control_service = DataControlService(db)
        deletion_counts = data_control_service.delete_user_data(user_id, request.data_categories)
        return DeleteDataResponse(
            deleted_counts=deletion_counts,
            deleted_at=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Statistics routes
@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """Get system statistics."""
    try:
        user_service = UserService(db)
        learning_service = LearningService(db)
        doc_service = DocumentationService(db)

        user_stats = user_service.get_user_statistics()
        learning_stats = learning_service.get_pattern_statistics()
        doc_stats = doc_service.get_documentation_stats()

        # Calculate deployment success rate
        from ..models import DeploymentLog
        total_deployments = db.query(DeploymentLog).count()
        successful_deployments = db.query(DeploymentLog).filter(
            DeploymentLog.status == "SUCCESS"
        ).count()

        success_rate = (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0

        return StatisticsResponse(
            total_users=user_stats.get("total_users", 0),
            active_users=user_stats.get("active_users", 0),
            total_submissions=user_stats.get("total_submissions", 0),
            successful_deployments=successful_deployments,
            total_deployments=total_deployments,
            success_rate=round(success_rate, 2),
            learning_patterns=learning_stats,
            documentation_stats=doc_stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handler should be added to the main FastAPI app, not the router