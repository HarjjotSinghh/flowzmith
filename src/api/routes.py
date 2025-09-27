"""
API routes for Flowzmith.
"""

import asyncio
import time
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
from ..cli.contract_creator import ContractCreator
from ..cli.api_client import APIClient
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
    ErrorResponse,
    ContextGenerationRequest,
    FlowProjectCreateRequest,
    FlowProjectResponse,
    FlowDeploymentRequest,
    FlowDeploymentResponse,
    FlowProjectStatusResponse,
    FlowGenerateDeployRequest,
    FlowDeploymentHistoryResponse,
    FlowDeploymentStatsResponse
)
from .schemas import HealthResponse

def strip_markdown_code_blocks(content: str) -> str:
    """Strip markdown code block syntax from contract content."""
    if not content:
        return content
    
    lines = content.strip().split('\n')
    
    # Remove first line if it starts with ```
    if lines and lines[0].strip().startswith('```'):
        lines = lines[1:]
    
    # Remove last line if it's just ```
    if lines and lines[-1].strip() == '```':
        lines = lines[:-1]
    
    return '\n'.join(lines)

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
            timestamp=datetime.utcnow().isoformat(),
            version="1.0.0",
            database_connected=db_connected,
            llm_providers=llm_providers,
            flow_cli_available=flow_cli_available
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Flow CLI Endpoints
@router.post("/flow/projects", response_model=FlowProjectResponse)
async def create_flow_project(
    request: FlowProjectCreateRequest,
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """Create a new Flow project using flow init command."""
    try:
        from ..cli.flow_manager import FlowProjectManager
        
        flow_manager = FlowProjectManager()
        
        project_name = request.name or f"FlowProject_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        contract_name = request.contract_type or "HelloWorld"
        
        # Create a basic contract content based on contract type
        contract_content = f"""
// {contract_name}.cdc
// A simple {contract_name} contract for Flow blockchain

access(all) contract {contract_name} {{
    access(all) var greeting: String

    init() {{
        self.greeting = "Hello, World!"
    }}

    access(all) fun hello(): String {{
        return self.greeting
    }}

    access(all) fun changeGreeting(newGreeting: String) {{
        self.greeting = newGreeting
    }}
}}
""".strip()
        
        result = await flow_manager.create_flow_project(
            project_id=project_name,
            contract_name=contract_name,
            contract_content=contract_content,
            network=request.network or "emulator"
        )
        
        if result.get("status") != "success":
            raise Exception(f"Project creation failed: {result.get('error', 'Unknown error')}")
        
        # Get project status
        status = await flow_manager.get_project_status(project_name)
        
        return FlowProjectResponse(
            project_id=str(uuid.uuid4()),
            name=project_name,
            path=result.get("project_dir", ""),
            network=request.network or "emulator",
            status="initialized",
            contracts=status.get("contracts", []),
            created_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Flow project: {str(e)}")


@router.post("/flow/deploy", response_model=FlowDeploymentResponse)
async def deploy_flow_contract(
    request: FlowDeploymentRequest,
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """Deploy contracts in a Flow project using flow project deploy."""
    try:
        from ..cli.flow_manager import FlowProjectManager
        
        flow_manager = FlowProjectManager()
        
        deployment_id = str(uuid.uuid4())
        started_at = datetime.now()
        
        result = await flow_manager.deploy_contracts(
            request.project_name, 
            request.network, 
            request.contract_name
        )
        
        return FlowDeploymentResponse(
            project_name=request.project_name,
            network=request.network,
            status="success" if result.get("success") else "failed",
            transaction_hash=result.get("transaction_hash"),
            deployed_at=datetime.now() if result.get("success") else None,
            error_message=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deploy contract: {str(e)}")


@router.get("/flow/projects/{project_path:path}/status", response_model=FlowProjectStatusResponse)
async def get_flow_project_status(
    project_path: str,
    db: Session = Depends(get_db)
):
    """Get status information for a Flow project."""
    try:
        from ..cli.flow_manager import FlowProjectManager
        
        flow_manager = FlowProjectManager()
        status = await flow_manager.get_project_status(project_path)
        
        return FlowProjectStatusResponse(
            project_path=project_path,
            name=status.get("name", "Unknown"),
            network=status.get("network", "emulator"),
            flow_json_exists=status.get("flow_json_exists", False),
            contracts_count=len(status.get("contracts", [])),
            contracts=status.get("contracts", []),
            emulator_running=status.get("emulator_running", False),
            last_deployment=status.get("last_deployment")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project status: {str(e)}")


@router.get("/flow/projects", response_model=List[FlowProjectResponse])
async def list_flow_projects(
    db: Session = Depends(get_db)
):
    """List all Flow projects in the flow_projects directory."""
    try:
        from ..cli.flow_manager import FlowProjectManager
        
        flow_manager = FlowProjectManager()
        projects = await flow_manager.list_projects()
        
        return [
            FlowProjectResponse(
                project_id=str(uuid.uuid4()),
                name=project["name"],
                path=project["path"],
                network=project.get("network", "emulator"),
                status="active",
                contracts=project.get("contracts", []),
                created_at=datetime.now(),  # Would be better to get from filesystem
                last_modified=project.get("last_modified")
            )
            for project in projects
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")


@router.post("/flow/generate-deploy", response_model=FlowDeploymentResponse)
async def generate_and_deploy_flow_contract(
    request: FlowGenerateDeployRequest,
    user_id: str = None,
    db: Session = Depends(get_db)
):
    """Generate a contract and automatically deploy it using Flow CLI."""
    try:
        from ..cli.deployment_service import ContractDeploymentService
        
        client = APIClient()
        deployment_service = ContractDeploymentService(client)
        
        project_name = request.project_name or f"Contract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        deployment_id = str(uuid.uuid4())
        started_at = datetime.now()
        
        # Generate contract
        generation_result = await client.generate_contract_from_context(
            requirements=request.requirements,
            context_dir=request.context_dir,
            network=request.network
        )
        
        if not generation_result.get("success"):
            return FlowDeploymentResponse(
                deployment_id=deployment_id,
                project_path="",
                contract_name=project_name,
                network=request.network,
                status="failed",
                error_message=f"Contract generation failed: {generation_result.get('error')}",
                started_at=started_at,
                completed_at=datetime.now()
            )
        
        # Deploy with Flow CLI if auto_deploy is enabled
        if request.auto_deploy:
            deployment_result = await deployment_service.deploy_with_flow_cli(
                generation_result.get("contract"),
                generation_result.get("flow_json"),
                project_name,
                request.network
            )
            
            return FlowDeploymentResponse(
                deployment_id=deployment_id,
                project_path=deployment_result.get("project_path", ""),
                contract_name=project_name,
                network=request.network,
                status="success" if deployment_result.get("success") else "failed",
                transaction_id=deployment_result.get("transaction_id"),
                error_message=deployment_result.get("error"),
                output=deployment_result.get("output"),
                started_at=started_at,
                completed_at=datetime.now()
            )
        else:
            # Just return generation success
            return FlowDeploymentResponse(
                deployment_id=deployment_id,
                project_path="",
                contract_name=project_name,
                network=request.network,
                status="generated",
                output="Contract generated successfully",
                started_at=started_at,
                completed_at=datetime.now()
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate and deploy contract: {str(e)}")


@router.get("/flow/deployments/history", response_model=FlowDeploymentHistoryResponse)
async def get_flow_deployment_history(
    limit: int = 50,
    network: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get Flow deployment history."""
    try:
        from ..cli.deployment_service import ContractDeploymentService
        
        client = APIClient()
        deployment_service = ContractDeploymentService(client)
        
        history = await deployment_service.get_deployment_history(limit, network)
        
        deployments = [
            FlowDeploymentResponse(
                deployment_id=dep["id"],
                project_path=dep.get("project_path", ""),
                contract_name=dep.get("contract_name"),
                network=dep["network"],
                status=dep["status"],
                transaction_id=dep.get("transaction_id"),
                error_message=dep.get("error_message"),
                output=dep.get("output"),
                started_at=dep["started_at"],
                completed_at=dep.get("completed_at")
            )
            for dep in history.get("deployments", [])
        ]
        
        return FlowDeploymentHistoryResponse(
            deployments=deployments,
            total_count=history.get("total_count", 0),
            success_count=history.get("success_count", 0),
            failure_count=history.get("failure_count", 0),
            success_rate=history.get("success_rate", 0.0)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get deployment history: {str(e)}")


@router.get("/flow/deployments/stats", response_model=FlowDeploymentStatsResponse)
async def get_flow_deployment_stats(
    db: Session = Depends(get_db)
):
    """Get Flow deployment statistics."""
    try:
        from ..cli.deployment_service import ContractDeploymentService
        from ..cli.flow_manager import FlowProjectManager
        
        client = APIClient()
        deployment_service = ContractDeploymentService(client)
        flow_manager = FlowProjectManager()
        
        stats = await deployment_service.get_deployment_stats()
        projects = await flow_manager.list_projects()
        
        recent_deployments = [
            FlowDeploymentResponse(
                deployment_id=dep["id"],
                project_path=dep.get("project_path", ""),
                contract_name=dep.get("contract_name"),
                network=dep["network"],
                status=dep["status"],
                transaction_id=dep.get("transaction_id"),
                error_message=dep.get("error_message"),
                output=dep.get("output"),
                started_at=dep["started_at"],
                completed_at=dep.get("completed_at")
            )
            for dep in stats.get("recent_deployments", [])
        ]
        
        return FlowDeploymentStatsResponse(
            total_projects=len(projects),
            total_deployments=stats.get("total_deployments", 0),
            successful_deployments=stats.get("successful_deployments", 0),
            failed_deployments=stats.get("failed_deployments", 0),
            success_rate=stats.get("success_rate", 0.0),
            networks=stats.get("networks", {}),
            recent_deployments=recent_deployments
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get deployment stats: {str(e)}")


@router.get("/flow/cli/status")
async def get_flow_cli_status(
    db: Session = Depends(get_db)
):
    """Check Flow CLI installation and status."""
    try:
        from ..cli.flow_manager import FlowProjectManager
        
        flow_manager = FlowProjectManager()
        status = await flow_manager.check_flow_cli()
        
        return {
            "flow_cli_installed": status.get("installed", False),
            "version": status.get("version"),
            "path": status.get("path"),
            "emulator_available": status.get("emulator_available", False)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check Flow CLI status: {str(e)}")

@router.post("/contracts/generate-flow-project")
async def generate_flow_project(
    contract_data: dict,
    user_id: str = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Generate a complete Flow project with contract, transactions, scripts, tests, and flow.json."""
    try:
        # Initialize API client and contract creator
        api_client = APIClient(base_url="http://localhost:8000")
        contract_creator = ContractCreator(api_client)
        
        # Prepare requirements from contract_data
        requirements = {
            "name": contract_data.get("contract_name", contract_data.get("name", "Contract")),
            "type": contract_data.get("contract_type", contract_data.get("type", "custom")),
            "description": contract_data.get("description", ""),
            "network": contract_data.get("network", "testnet"),
            "metadata": contract_data.get("metadata", {})
        }
        
        # Get contract content
        contract_content = contract_data.get("content", "")
        input_method = contract_data.get("input_method", "api")
        
        # Create a mock result object for file generation
        result = {
            "contract_id": str(uuid.uuid4()),
            "status": "success",
            "contract_code": contract_content,
            "message": "Contract generated successfully"
        }
        
        # Generate and save all files using the ContractCreator
        project_path = await contract_creator._save_contract_to_filesystem(
            result, requirements, contract_content, input_method
        )
        
        # Save to database as well
        await contract_creator._save_contract_to_database(
            result, requirements, contract_content, input_method, 0.0
        )
        
        # Get the generated files information
        from pathlib import Path
        project_dir = Path(project_path)
        
        # Collect information about generated files
        generated_files = {
            "contract": None,
            "flow_json": None,
            "transactions": [],
            "scripts": [],
            "tests": []
        }
        
        # Check for contract file
        contracts_dir = project_dir / "contracts"
        if contracts_dir.exists():
            for file in contracts_dir.glob("*.cdc"):
                generated_files["contract"] = str(file.relative_to(project_dir))
                break
        
        # Check for flow.json
        flow_json = project_dir / "flow.json"
        if flow_json.exists():
            generated_files["flow_json"] = "flow.json"
        
        # Check for transactions
        transactions_dir = project_dir / "transactions"
        if transactions_dir.exists():
            generated_files["transactions"] = [
                str(file.relative_to(project_dir)) 
                for file in transactions_dir.glob("*.cdc")
            ]
        
        # Check for scripts
        scripts_dir = project_dir / "scripts"
        if scripts_dir.exists():
            generated_files["scripts"] = [
                str(file.relative_to(project_dir)) 
                for file in scripts_dir.glob("*.cdc")
            ]
        
        # Check for tests
        tests_dir = project_dir / "tests"
        if tests_dir.exists():
            generated_files["tests"] = [
                str(file.relative_to(project_dir)) 
                for file in tests_dir.glob("*.cdc")
            ]
        
        return {
            "status": "success",
            "message": "Flow project generated successfully",
            "contract_id": result["contract_id"],
            "project_path": project_path,
            "project_directory": project_dir.name,
            "generated_files": generated_files,
            "requirements": requirements,
            "input_method": input_method
        }
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate Flow project: {str(e)}\n{traceback.format_exc()}"
        )

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
    user_id: str = None,
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

        # Save files locally using ContractCreator for comprehensive file generation
        saved_locally = False
        generated_files = {}
        try:
            # Initialize ContractCreator and APIClient
            api_client = APIClient()
            contract_creator = ContractCreator(api_client, db)
            
            # Create a mock result object with the generated contract
            class MockResult:
                def __init__(self, contract_code, config_content):
                    self.generated_contract_code = contract_code
                    self.config_content = config_content
                    self.generated_files = {
                        'flow.json': config_content,
                        'transactions': {},
                        'scripts': {},
                        'tests': {}
                    }
            
            mock_result = MockResult(generated_config.generated_contract_code, generated_config.config_content)
            
            # Use ContractCreator to save comprehensive project files
            project_path = contract_creator._save_contract_to_filesystem(
                mock_result,
                str(submission.id),
                request.requirements
            )
            
            # Also save to database
            contract_creator._save_contract_to_database(
                mock_result,
                str(submission.id),
                request.requirements,
                resolved_user.id
            )
            
            saved_locally = True
            generated_files = {
                'project_path': str(project_path),
                'contract_file': f"{project_path}/contracts/SmartContract.cdc",
                'flow_json': f"{project_path}/flow.json",
                'transactions_dir': f"{project_path}/transactions",
                'scripts_dir': f"{project_path}/scripts",
                'tests_dir': f"{project_path}/tests"
            }
        except Exception as e:
            # Fallback manual save if ContractCreator fails
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
                    f.write(strip_markdown_code_blocks(generated_config.generated_contract_code))
                with open(proj / "flow.json", "w") as f:
                    json.dump(generated_config.config_content, f, indent=2)
                saved_locally = True
                generated_files = {
                    'project_path': str(proj),
                    'contract_file': f"{proj}/contracts/{contract_name}.cdc",
                    'flow_json': f"{proj}/flow.json"
                }
            except Exception:
                saved_locally = False

        # No deployment here; just return the generation results
        response = ContractGenerationResponse(
            submission_id=submission.id,
            config_id=generated_config.id,
            generated_contract_code=generated_config.generated_contract_code,
            config_content=generated_config.config_content,
            validation_status=generated_config.validation_status,
            deployment_logs=[]
        )
        
        # Add generated files information to config_content for client access
        if saved_locally and generated_files:
            response.config_content["generated_files"] = generated_files
            response.config_content["project_saved"] = True
        else:
            response.config_content["project_saved"] = False
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/submit")
async def submit_contract(
    contract_data: dict,
    user_id: str = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Submit contract data for processing and generate all files."""
    try:
        # Create submission from contract data
        from ..models import ContractSubmission, InputType, SubmissionStatus, User, PersonaType
        import uuid as _uuid
        import time

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

        # Now actually generate the contract files like the CLI does
        generation_start_time = time.time()
        
        # Initialize ContractCreator and APIClient for file generation
        api_client = APIClient(base_url="http://localhost:8000")
        contract_creator = ContractCreator(api_client, db)
        
        # Prepare requirements from contract_data
        requirements = {
            "name": contract_data.get("name", contract_data.get("contract_name", "Contract")),
            "type": contract_data.get("type", contract_data.get("contract_type", "custom")).lower(),
            "description": contract_data.get("description", ""),
            "network": contract_data.get("network", "testnet"),
            "metadata": contract_data.get("metadata", {}),
            "account_setup": contract_data.get("account_setup", "single"),
            "features": contract_data.get("features", ["transactions", "deployment_scripts", "test_cases"])
        }
        
        # Get contract content
        contract_content = contract_data.get("content", "")
        input_method = "api"
        
        # Create a mock result object for file generation
        contract_id = str(uuid.uuid4())
        result = {
            "contract_id": contract_id,
            "submission_id": str(submission.id),
            "status": "success",
            "contract_code": contract_content,
            "flow_project": contract_data.get("flow_project", {}),
            "message": "Contract generated successfully"
        }
        
        # Generate and save all files using the ContractCreator methods
        project_path = await contract_creator._save_contract_to_filesystem(
            result, requirements, contract_content, input_method
        )
        
        # Calculate generation time
        generation_time = time.time() - generation_start_time
        
        # Read the generated metadata to get file information for database storage
        try:
            from pathlib import Path
            import json
            metadata_file = Path(project_path) / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    files_generated = metadata.get("files_generated", {})
                    
                    # Update result object with flow project information
                    result["flow_project"] = {
                        "transactions": files_generated.get("transactions", []),
                        "scripts": files_generated.get("scripts", []),
                        "tests": files_generated.get("tests", []),
                        "flow_json": files_generated.get("flow_json", ""),
                        "contract": files_generated.get("contract", "")
                    }
        except Exception as e:
            # Silently continue if metadata cannot be read
            pass
        
        # Save to database as well
        await contract_creator._save_contract_to_database(
            result, requirements, contract_content, input_method, generation_time
        )
        
        # Update submission status to completed
        submission.status = SubmissionStatus.COMPLETED
        db.commit()

        return {
            "submission_id": str(submission.id),
            "user_id": str(resolved_user.id),
            "status": "success",
            "message": "Contract submitted and files generated successfully",
            "project_path": project_path,
            "generation_time": generation_time
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
    user_id: str = None,
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
        # Ensure attributes are loaded and available post-commit
        db.refresh(submission)

        async def generate_stream(): 
            """Stream the contract generation process."""
            from ..services.streaming_llm_provider import StreamingProgressTracker
            from ..models.database import SessionLocal
            import json

            # Create a dedicated DB session for streaming lifecycle
            stream_db = SessionLocal()
            # Attach submission to the streaming session to avoid detached instance issues
            submission_stream = stream_db.merge(submission)
            # Use a dedicated LLMService bound to the streaming session
            llm_service_stream = LLMService(stream_db)
            
            # Create progress tracker
            progress_tracker = StreamingProgressTracker(
                total_steps=100,
                description="Generating smart contract"
            )
            
            try:
                # Start streaming contract generation
                contract_content = ""
                config_content = None
                
                async for chunk in llm_service_stream.generate_contract_with_external_context_streaming(
                    submission_stream,
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
                    flow_service = FlowService(stream_db)
                    project_path = flow_service.create_project_structure(str(submission_stream.id))
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
                        proj = _Path(settings.flow_projects_path) / str(submission_stream.id)
                        (proj / "contracts").mkdir(parents=True, exist_ok=True)
                        (proj / "transactions").mkdir(exist_ok=True)
                        (proj / "scripts").mkdir(exist_ok=True)
                        contract_name = "SmartContract"  # Default name
                        with open(proj / "contracts" / f"{contract_name}.cdc", "w") as f:
                            f.write(strip_markdown_code_blocks(contract_content))
                        with open(proj / "flow.json", "w") as f:
                            json.dump(json.loads(config_content) if config_content else {}, f, indent=2)
                        saved_locally = True
                    except Exception:
                        saved_locally = False
                
                progress_tracker.update_phase("saving_files", 1.0)
                
                # Send final status
                final_status = {
                    "submission_id": str(submission_stream.id),
                    "saved_locally": saved_locally,
                    "status": "completed"
                }
                yield f"\n<!-- FINAL_STATUS:{json.dumps(final_status)} -->\n"
                
            except Exception as e:
                error_msg = f"Error during streaming generation: {str(e)}"
                yield f"\n<!-- ERROR:{error_msg} -->\n"
                raise
            finally:
                try:
                    stream_db.close()
                except Exception:
                    pass
                progress_tracker.complete()

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