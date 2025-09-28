from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from src.models.database import get_db
from src.services.user_service import UserService
from src.services.llm_service import LLMService
from src.services.flow_service import FlowService
from src.services.learning_service import LearningService
from src.models.user import User
from src.models.contract import ContractSubmission, Deployment
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json

router = APIRouter()

# Initialize services
user_service = UserService()
llm_service = LLMService()
flow_service = FlowService()
learning_service = LearningService()

# Pydantic models for request/response
class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str
    persona_type: str

class UserLogin(BaseModel):
    email: str
    password: str

class ContractRequest(BaseModel):
    input_type: str
    content: str
    pre_conditions: Optional[Dict[str, Any]] = None
    post_conditions: Optional[Dict[str, Any]] = None
    network: str = "testnet"

class DeployRequest(BaseModel):
    network: str = "testnet"
    config_id: Optional[str] = None

class DocumentationSearch(BaseModel):
    query: str
    limit: int = 10
    use_semantic_search: bool = True

# Dependency to get current user
async def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = user_service.verify_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = user_service.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user

# User Management endpoints
@router.post("/users")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        user = user_service.create_user(
            db=db,
            email=user_data.email,
            full_name=user_data.full_name,
            password=user_data.password,
            persona_type=user_data.persona_type
        )
        return {"message": "User created successfully", "user_id": user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/login")
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = user_service.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Contract Generation endpoints
@router.post("/contracts")
async def generate_contract(
    contract_data: ContractRequest,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token, db)

    try:
        # Generate contract using LLM
        generated_contract = await llm_service.generate_contract(
            prompt=contract_data.content,
            context={
                "pre_conditions": contract_data.pre_conditions,
                "post_conditions": contract_data.post_conditions,
                "network": contract_data.network
            }
        )

        # Save submission to database
        submission = ContractSubmission(
            user_id=current_user.id,
            input_type=contract_data.input_type,
            content=contract_data.content,
            generated_contract=generated_contract,
            pre_conditions=contract_data.pre_conditions,
            post_conditions=contract_data.post_conditions,
            network=contract_data.network,
            status="GENERATED"
        )

        db.add(submission)
        db.commit()
        db.refresh(submission)

        return {
            "submission_id": submission.id,
            "generated_contract": generated_contract,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/contracts/file")
async def upload_contract_file(
    file: UploadFile = File(...),
    token: str = None,
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(('.cdc', '.sol')):
        raise HTTPException(status_code=400, detail="Only .cdc and .sol files are supported")

    try:
        content = await file.read()
        contract_code = content.decode('utf-8')

        # Save submission to database
        submission = ContractSubmission(
            user_id=1 if not token else (await get_current_user(token, db)).id,
            input_type="FILE_UPLOAD",
            content=contract_code,
            generated_contract=contract_code,
            network="testnet",
            status="UPLOADED"
        )

        db.add(submission)
        db.commit()
        db.refresh(submission)

        return {
            "submission_id": submission.id,
            "message": "Contract uploaded successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Deployment endpoints
@router.post("/contracts/{submission_id}/deploy")
async def deploy_contract(
    submission_id: int,
    deploy_data: DeployRequest,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token, db)

    # Get submission
    submission = db.query(ContractSubmission).filter(
        ContractSubmission.id == submission_id,
        ContractSubmission.user_id == current_user.id
    ).first()

    if not submission:
        raise HTTPException(status_code=404, detail="Contract submission not found")

    try:
        # Deploy contract
        deployment_result = await flow_service.deploy_contract(
            contract_code=submission.generated_contract,
            contract_name=f"Contract_{submission_id}",
            network=deploy_data.network
        )

        # Save deployment record
        deployment = Deployment(
            submission_id=submission_id,
            network=deploy_data.network,
            transaction_hash=deployment_result.get("transaction_hash"),
            contract_address=deployment_result.get("contract_address"),
            gas_used=deployment_result.get("gas_used"),
            status="DEPLOYED" if deployment_result["success"] else "FAILED",
            error_message=deployment_result.get("error_message") if not deployment_result["success"] else None
        )

        db.add(deployment)
        db.commit()
        db.refresh(deployment)

        return deployment_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contracts/{submission_id}/deployments/{deployment_id}")
async def get_deployment_status(
    submission_id: int,
    deployment_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(token, db)

    deployment = db.query(Deployment).join(ContractSubmission).filter(
        Deployment.id == deployment_id,
        ContractSubmission.id == submission_id,
        ContractSubmission.user_id == current_user.id
    ).first()

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return {
        "id": deployment.id,
        "submission_id": deployment.submission_id,
        "network": deployment.network,
        "transaction_hash": deployment.transaction_hash,
        "contract_address": deployment.contract_address,
        "status": deployment.status,
        "gas_used": deployment.gas_used,
        "error_message": deployment.error_message,
        "created_at": deployment.created_at
    }

# Documentation endpoints
@router.post("/documentation/search")
async def search_documentation(search_data: DocumentationSearch, db: Session = Depends(get_db)):
    results = await learning_service.search_documentation(
        db=db,
        query=search_data.query,
        limit=search_data.limit,
        use_semantic_search=search_data.use_semantic_search
    )
    return results

@router.get("/documentation/stats")
async def get_documentation_stats(db: Session = Depends(get_db)):
    return learning_service.get_documentation_stats(db)

# Learning & Analytics endpoints
@router.get("/learning/insights")
async def get_learning_insights(token: str, db: Session = Depends(get_db)):
    current_user = await get_current_user(token, db)
    insights = learning_service.get_user_insights(db, current_user.id)
    return insights

@router.get("/statistics")
async def get_system_statistics(token: str, db: Session = Depends(get_db)):
    current_user = await get_current_user(token, db)

    # Get various statistics
    total_submissions = db.query(ContractSubmission).filter(
        ContractSubmission.user_id == current_user.id
    ).count()

    total_deployments = db.query(Deployment).join(ContractSubmission).filter(
        ContractSubmission.user_id == current_user.id
    ).count()

    successful_deployments = db.query(Deployment).join(ContractSubmission).filter(
        ContractSubmission.user_id == current_user.id,
        Deployment.status == "DEPLOYED"
    ).count()

    return {
        "total_submissions": total_submissions,
        "total_deployments": total_deployments,
        "successful_deployments": successful_deployments,
        "success_rate": successful_deployments / total_deployments if total_deployments > 0 else 0
    }