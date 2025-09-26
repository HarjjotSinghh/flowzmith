"""
API routes for Smart Contract LLM Builder.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
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
    ErrorResponse,
    ContextGenerationRequest
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

# Context-based contract generation route
@router.post("/contracts/generate-with-context", response_model=ContractGenerationResponse)
async def generate_contract_with_context(
    request: ContextGenerationRequest,
    user_id: str,
    request_ctx: Request = None,
    db: Session = Depends(get_db)
):
    """Generate contract using external markdown context and save locally."""
    try:
        # Initialize services (FlowService lazily due to potential CLI absence)
        user_service = UserService(db)
        llm_service = LLMService(db)

        # Resolve or create user (similar to /contracts)
        from ..models import User, PersonaType, ContractSubmission, InputType
        import uuid as _uuid
        from ..config import get_settings as _get_settings

        resolved_user = None
        try:
            provided_user_uuid = _uuid.UUID(user_id)
            resolved_user = db.query(User).filter(User.id == provided_user_uuid).first()
        except Exception:
            resolved_user = None

        if not resolved_user:
            client_ip = None
            try:
                client_ip = request_ctx.client.host if request_ctx and request_ctx.client else None
            except Exception:
                client_ip = None

            if client_ip:
                synthetic_email = f"ip-{str(client_ip).replace(':', '-') }@local"
            else:
                synthetic_email = f"anonymous-{_uuid.uuid4()}@local"

            resolved_user = db.query(User).filter(User.email == synthetic_email).first()
            if not resolved_user:
                resolved_user = User(
                    email=synthetic_email,
                    persona_type=PersonaType.NON_TECHNICAL,
                    preferences={"source": "api", "identifier": client_ip},
                    data_retention_consent=False
                )
                db.add(resolved_user)
                db.commit()
                db.refresh(resolved_user)

        # Create a submission using NATURAL_LANGUAGE with provided requirements
        submission = ContractSubmission(
            user_id=resolved_user.id,
            input_type=InputType.NATURAL_LANGUAGE,
            content=request.requirements,
            pre_conditions=request.pre_conditions,
            post_conditions=request.post_conditions
        )
        db.add(submission)
        db.commit()

        # Generate contract with external context
        generated_config = await llm_service.generate_contract_with_external_context(
            submission,
            external_context=request.context or ""
        )

        # Validate configuration
        await llm_service.validate_configuration(generated_config)

        # Save files locally regardless of deployment
        saved_locally = False
        try:
            flow_service = FlowService(db)
            project_path = flow_service.create_project_structure(str(submission.id))
            flow_service.save_contract_files(
                project_path,
                generated_config.generated_contract_code,
                generated_config.config_content
            )
            saved_locally = True
        except Exception:
            # Fallback manual save if Flow CLI is unavailable
            try:
                settings = _get_settings()
                import os, json
                from pathlib import Path as _Path
                proj = _Path(settings.flow_projects_path) / str(submission.id)
                (proj / "contracts").mkdir(parents=True, exist_ok=True)
                (proj / "transactions").mkdir(exist_ok=True)
                (proj / "scripts").mkdir(exist_ok=True)
                contract_name = generated_config.config_content.get("contracts", {}).get("default") or "SmartContract"
                with open(proj / "contracts" / f"{contract_name}.cdc", "w") as f:
                    f.write(generated_config.generated_contract_code)
                with open(proj / "flow.json", "w") as f:
                    json.dump(generated_config.config_content, f, indent=2)
                saved_locally = True
            except Exception:
                saved_locally = False

        # No deployment here; just return the generation results
        return ContractGenerationResponse(
            submission_id=submission.id,
            config_id=generated_config.id,
            generated_contract_code=generated_config.generated_contract_code,
            config_content=generated_config.config_content,
            validation_status=generated_config.validation_status,
            deployment_logs=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/submit")
async def submit_contract(
    contract_data: dict,
    user_id: str = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Submit contract data for processing."""
    try:
        # Create submission from contract data
        from ..models import ContractSubmission, InputType, SubmissionStatus, User, PersonaType
        import uuid as _uuid

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

        # Resolve or create user
        resolved_user = None
        provided_user_uuid = None
        if user_id:
            try:
                provided_user_uuid = _uuid.UUID(user_id)
                resolved_user = db.query(User).filter(User.id == provided_user_uuid).first()
            except ValueError:
                provided_user_uuid = None
                resolved_user = None

        # Determine source and identifier
        system_address = contract_data.get("system_address") or contract_data.get("mac_address")
        client_ip = None
        try:
            client_ip = request.client.host if request and request.client else None
        except Exception:
            client_ip = None

        # Build synthetic email based on source
        if system_address:
            identifier = str(system_address).lower().replace(":", "-").replace(" ", "")
            synthetic_email = f"cli-{identifier}@local"
        elif client_ip:
            identifier = str(client_ip).replace(":", "-")
            synthetic_email = f"ip-{identifier}@local"
        else:
            synthetic_email = f"anonymous-{_uuid.uuid4()}@local"

        if not resolved_user:
            # Try to find by synthetic email
            resolved_user = db.query(User).filter(User.email == synthetic_email).first()

        if not resolved_user:
            # Create minimal user record to satisfy FK
            resolved_user = User(
                email=synthetic_email,
                persona_type=PersonaType.NON_TECHNICAL,
                preferences={
                    "source": "cli" if system_address else "api",
                    "identifier": system_address or client_ip
                },
                data_retention_consent=False
            )
            db.add(resolved_user)
            db.commit()
            db.refresh(resolved_user)

        submission = ContractSubmission(
            user_id=resolved_user.id,
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
            "user_id": str(resolved_user.id),
            "status": "success",
            "message": "Contract submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contracts/file")
async def upload_contract_file(
    file: UploadFile = File(...),
    user_id: str = None,
    system_address: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Upload contract file for processing."""
    try:
        if not file.filename.endswith(('.cdc', '.sol')):
            raise HTTPException(status_code=400, detail="Only .cdc and .sol files are supported")

        content = await file.read()
        content_str = content.decode('utf-8')

        # Determine input type
        from ..models import InputType, SubmissionStatus, ContractSubmission, User, PersonaType
        input_type = InputType.CDC_FILE if file.filename.endswith('.cdc') else InputType.SOL_FILE

        # Resolve or create user (use MAC/system address for CLI if provided; otherwise IP for web uploads)
        resolved_user = None
        import uuid as _uuid
        if user_id:
            try:
                provided_user_uuid = _uuid.UUID(user_id)
                resolved_user = db.query(User).filter(User.id == provided_user_uuid).first()
            except ValueError:
                resolved_user = None

        client_ip = None
        try:
            client_ip = request.client.host if request and request.client else None
        except Exception:
            client_ip = None

        if system_address:
            identifier = str(system_address).lower().replace(":", "-").replace(" ", "")
            synthetic_email = f"cli-{identifier}@local"
        else:
            synthetic_email = f"ip-{str(client_ip).replace(':', '-')}@local" if client_ip else f"anonymous-{_uuid.uuid4()}@local"

        if not resolved_user:
            resolved_user = db.query(User).filter(User.email == synthetic_email).first()
        if not resolved_user:
            resolved_user = User(
                email=synthetic_email,
                persona_type=PersonaType.NON_TECHNICAL,
                preferences={"source": "cli" if system_address else "api", "identifier": system_address or client_ip},
                data_retention_consent=False
            )
            db.add(resolved_user)
            db.commit()
            db.refresh(resolved_user)

        submission = ContractSubmission(
            user_id=resolved_user.id,
            input_type=input_type,
            content=content_str,
            pre_conditions={"filename": file.filename},
            status=SubmissionStatus.PENDING
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        return {
            "submission_id": str(submission.id),
            "user_id": str(resolved_user.id),
            "status": "success",
            "message": "File uploaded and contract submitted successfully"
        }
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

# Streaming contract generation endpoint
@router.post("/contracts/generate-with-context/streaming")
async def generate_contract_with_context_streaming(
    request: ContextGenerationRequest,
    user_id: str,
    request_ctx: Request = None,
    db: Session = Depends(get_db)
):
    """Generate contract using external markdown context with streaming."""
    try:
        # Initialize services
        user_service = UserService(db)
        llm_service = LLMService(db)

        # Resolve or create user
        from ..models import User, PersonaType, ContractSubmission, InputType
        import uuid as _uuid
        from ..config import get_settings as _get_settings

        resolved_user = None
        try:
            provided_user_uuid = _uuid.UUID(user_id)
            resolved_user = db.query(User).filter(User.id == provided_user_uuid).first()
        except Exception:
            resolved_user = None

        if not resolved_user:
            client_ip = None
            try:
                client_ip = request_ctx.client.host if request_ctx and request_ctx.client else None
            except Exception:
                client_ip = None

            if client_ip:
                synthetic_email = f"ip-{str(client_ip).replace(':', '-') }@local"
            else:
                synthetic_email = f"anonymous-{_uuid.uuid4()}@local"

            resolved_user = db.query(User).filter(User.email == synthetic_email).first()
            if not resolved_user:
                resolved_user = User(
                    email=synthetic_email,
                    persona_type=PersonaType.NON_TECHNICAL,
                    preferences={"source": "api", "identifier": client_ip},
                    data_retention_consent=False
                )
                db.add(resolved_user)
                db.commit()
                db.refresh(resolved_user)

        # Create a submission using NATURAL_LANGUAGE with provided requirements
        submission = ContractSubmission(
            user_id=resolved_user.id,
            input_type=InputType.NATURAL_LANGUAGE,
            content=request.requirements,
            pre_conditions=request.pre_conditions,
            post_conditions=request.post_conditions
        )
        db.add(submission)
        db.commit()

        async def generate_stream():
            """Stream the contract generation process."""
            from ..services.streaming_llm_provider import StreamingProgressTracker
            
            # Create progress tracker
            progress_tracker = StreamingProgressTracker(
                total_phases=3,  # generating_contract, generating_config, saving_files
                description="Generating smart contract"
            )
            
            try:
                # Start streaming contract generation
                contract_content = ""
                config_content = None
                
                async for chunk in llm_service.generate_contract_with_external_context_streaming(
                    submission,
                    external_context=request.context or "",
                    progress_tracker=progress_tracker
                ):
                    # Check if this is configuration data
                    if "<!-- CONFIG_START -->" in chunk:
                        # Extract config content
                        config_start = chunk.find("<!-- CONFIG_START -->") + len("<!-- CONFIG_START -->")
                        config_end = chunk.find("<!-- CONFIG_END -->")
                        if config_start > 0 and config_end > 0:
                            config_content = chunk[config_start:config_end]
                            # Don't send the config markers to the client
                            continue
                    
                    contract_content += chunk
                    yield chunk
                
                # Update progress for file saving
                progress_tracker.update_phase("saving_files", 0.0)
                
                # Save files locally
                saved_locally = False
                try:
                    flow_service = FlowService(db)
                    project_path = flow_service.create_project_structure(str(submission.id))
                    flow_service.save_contract_files(
                        project_path,
                        contract_content,
                        json.loads(config_content) if config_content else {}
                    )
                    saved_locally = True
                except Exception:
                    # Fallback manual save if Flow CLI is unavailable
                    try:
                        settings = _get_settings()
                        proj = Path(settings.flow_projects_path) / str(submission.id)
                        (proj / "contracts").mkdir(parents=True, exist_ok=True)
                        (proj / "transactions").mkdir(exist_ok=True)
                        (proj / "scripts").mkdir(exist_ok=True)
                        contract_name = "SmartContract"  # Default name
                        with open(proj / "contracts" / f"{contract_name}.cdc", "w") as f:
                            f.write(contract_content)
                        with open(proj / "flow.json", "w") as f:
                            json.dump(json.loads(config_content) if config_content else {}, f, indent=2)
                        saved_locally = True
                    except Exception:
                        saved_locally = False
                
                progress_tracker.update_phase("saving_files", 1.0)
                
                # Send final status
                final_status = {
                    "submission_id": str(submission.id),
                    "saved_locally": saved_locally,
                    "status": "completed"
                }
                yield f"\n<!-- FINAL_STATUS:{json.dumps(final_status)} -->\n"
                
            except Exception as e:
                error_msg = f"Error during streaming generation: {str(e)}"
                yield f"\n<!-- ERROR:{error_msg} -->\n"
                raise
            finally:
                progress_tracker.close()

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))