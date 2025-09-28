"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum

# Import model enums for use in schemas
from ..models import (
    InputType,
    SubmissionStatus,
    ValidationStatus,
    DeploymentStatus,
    ApprovalStatus,
    PatternType,
    ContentType,
    PersonaType,
    DataRetentionPreference,
    TransactionType
)


# User Schemas
class UserBase(BaseModel):
    email: str
    username: str
    persona_type: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Contract Schemas
class ContractSubmissionBase(BaseModel):
    description: str
    network: str
    pre_conditions: Optional[Dict[str, Any]] = {}
    post_conditions: Optional[Dict[str, Any]] = {}


class ContractSubmissionCreate(ContractSubmissionBase):
    pass


class ContractSubmissionResponse(ContractSubmissionBase):
    id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GeneratedConfigurationResponse(BaseModel):
    id: UUID
    submission_id: UUID
    validation_status: str
    llm_metadata: Dict[str, Any]
    generated_config: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# Deployment Schemas
class DeploymentLogResponse(BaseModel):
    id: UUID
    submission_id: UUID
    status: str
    network: str
    transaction_hash: Optional[str]
    gas_used: Optional[int]
    error_message: Optional[str]
    logs: List[Dict[str, Any]]
    deployed_at: datetime

    class Config:
        from_attributes = True


class TransactionProposalBase(BaseModel):
    submission_id: UUID
    transaction_type: str
    payload: Dict[str, Any]
    estimated_gas: Optional[int]


class TransactionProposalCreate(TransactionProposalBase):
    pass


class TransactionProposalResponse(TransactionProposalBase):
    id: UUID
    status: str
    approval_status: str
    created_at: datetime
    executed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Documentation Schemas
class DocumentationSearchRequest(BaseModel):
    query: str
    content_type: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)


class DocumentationSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_count: int
    query: str


class DocumentationResponse(BaseModel):
    id: UUID
    title: str
    content_type: str
    content: str
    source: str
    last_updated: datetime

    class Config:
        from_attributes = True


# Learning Schemas
class LearningFeedbackResponse(BaseModel):
    id: UUID
    pattern_type: str
    insights: Dict[str, Any]
    confidence_score: float
    created_at: datetime

    class Config:
        from_attributes = True


# Data Control Schemas
class DataExportRequest(BaseModel):
    data_types: List[str]
    format: str = Field(default="json", pattern="^(json|csv)$")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class DataExportResponse(BaseModel):
    download_url: str
    file_size: int
    created_at: datetime


class DataDeletionRequest(BaseModel):
    data_types: List[str]
    confirmation: bool = Field(default=False)


class DataDeletionResponse(BaseModel):
    deleted_items: int
    affected_data_types: List[str]
    completed_at: datetime


# Data Control Schemas
class DataControlUpdate(BaseModel):
    retention_preference: Optional[str] = None
    data_sharing_allowed: Optional[bool] = None


class DataControlResponse(BaseModel):
    user_id: UUID
    retention_preference: str
    data_sharing_allowed: bool
    last_updated: datetime

    class Config:
        from_attributes = True


class ExportRequest(BaseModel):
    data_types: List[str]
    format: str = Field(default="json", pattern="^(json|csv)$")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ExportResponse(BaseModel):
    export_id: UUID
    download_url: str
    file_size: int
    status: str
    created_at: datetime


class DeleteDataRequest(BaseModel):
    data_types: List[str]
    confirmation: bool
    reason: Optional[str] = None


class DeleteDataResponse(BaseModel):
    deleted_items: int
    affected_data_types: List[str]
    status: str
    completed_at: datetime


# Contract Generation Schemas
class ContextGenerationRequest(BaseModel):
    requirements: str
    context: str = ""
    pre_conditions: Optional[Dict[str, Any]] = {}
    post_conditions: Optional[Dict[str, Any]] = {}
    network: str = "emulator"


class ContractGenerationRequest(BaseModel):
    description: str
    network: str = "testnet"
    pre_conditions: Optional[Dict[str, Any]] = {}
    post_conditions: Optional[Dict[str, Any]] = {}


class ContractGenerationResponse(BaseModel):
    submission_id: UUID
    config_id: UUID
    generated_contract_code: str
    config_content: Dict[str, Any]
    validation_status: str
    deployment_logs: List[Dict[str, Any]]


class DeploymentRequest(BaseModel):
    submission_id: UUID
    network: str = "testnet"
    gas_limit: Optional[int] = None


class DeploymentResponse(BaseModel):
    deployment_id: UUID
    status: str
    transaction_hash: Optional[str]
    network: str
    gas_used: Optional[int]
    deployed_at: Optional[datetime]


class TransactionApprovalRequest(BaseModel):
    transaction_id: UUID
    approved: bool
    comment: Optional[str] = None


# Statistics Schemas
class StatisticsResponse(BaseModel):
    total_contracts: int
    successful_deployments: int
    active_users: int
    average_generation_time: float
    uptime_percentage: float


# Error Response Schema
class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int
    timestamp: str
    details: Optional[Dict[str, Any]] = None


# WebSocket Schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime


class WebSocketResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime


class ProgressUpdate(BaseModel):
    submission_id: UUID
    stage: str
    progress: float = Field(ge=0.0, le=1.0)
    message: Optional[str] = None
    estimated_completion: Optional[datetime] = None


class EventBroadcast(BaseModel):
    event_type: str
    data: Dict[str, Any]
    target_users: Optional[List[UUID]] = None
    timestamp: datetime


class LogUpdate(BaseModel):
    submission_id: UUID
    log_level: str = Field(pattern="^(DEBUG|INFO|WARNING|ERROR)$")
    message: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class StatusUpdate(BaseModel):
    submission_id: UUID
    status: str
    message: Optional[str] = None
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


# General Response Schemas
class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: str


class APIInfoResponse(BaseModel):
    name: str
    version: str
    description: str
    features: List[str]
    endpoints: Dict[str, str]


# Flow CLI Schemas
class FlowProjectCreateRequest(BaseModel):
    name: str
    contract_type: str = "HelloWorld"
    network: str = "emulator"
    directory: Optional[str] = None
    description: Optional[str] = None


class FlowProjectResponse(BaseModel):
    name: str
    path: str
    status: str
    network: str
    contracts: List[Dict[str, Any]]
    created_at: datetime


class FlowDeploymentRequest(BaseModel):
    project_name: str
    network: str = "emulator"
    contract_name: Optional[str] = None


class FlowDeploymentResponse(BaseModel):
    project_name: str
    network: str
    status: str
    transaction_hash: Optional[str] = None
    deployed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class FlowProjectStatusResponse(BaseModel):
    project_name: str
    path: str
    status: str
    network: str
    contracts: List[Dict[str, Any]]
    flow_config: Dict[str, Any]


class FlowGenerateDeployRequest(BaseModel):
    requirements: str
    context_dir: Optional[str] = None
    network: str = "emulator"
    project_name: Optional[str] = None


class FlowDeploymentHistoryResponse(BaseModel):
    deployments: List[Dict[str, Any]]
    total_count: int
    page: int
    limit: int


class FlowDeploymentStatsResponse(BaseModel):
    total_deployments: int
    successful_deployments: int
    failed_deployments: int
    networks: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


# MCP Explorer Schemas
class MCPAccountResponse(BaseModel):
    """Schema for MCP account response."""
    address: str
    balance: Optional[str] = None
    keys: Optional[List[Dict[str, Any]]] = None
    contracts: Optional[Dict[str, Any]] = None


class MCPContractResponse(BaseModel):
    """Schema for MCP contract response."""
    address: str
    name: str
    code: Optional[str] = None
    events: Optional[List[Dict[str, Any]]] = None


class MCPTransactionResponse(BaseModel):
    """Schema for MCP transaction response."""
    id: str
    status: str
    block_id: Optional[str] = None
    block_height: Optional[int] = None
    events: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None


# System Setup Schemas
class SystemSetupResponse(BaseModel):
    """Schema for system setup response."""
    database_connected: bool
    llm_providers: List[str]
    flow_cli_available: bool
    setup_complete: bool


class SystemVersionResponse(BaseModel):
    """Schema for system version response."""
    name: str
    version: str
    description: str
    github: str


# Documentation Upload Schemas
class DocumentationUploadResponse(BaseModel):
    """Schema for documentation upload response."""
    uploaded_files: List[Dict[str, Any]]
    total_uploaded: int


class DocumentationCategoriesResponse(BaseModel):
    """Schema for documentation categories response."""
    categories: Dict[str, Any]


# Contract Wizard Schemas
class ContractWizardRequest(BaseModel):
    """Schema for contract wizard request."""
    input_method: Optional[str] = "natural_language"
    requirements: Optional[Dict[str, Any]] = None
    auto_deploy: bool = False
    network: str = Field("emulator", pattern=r'^(testnet|mainnet|emulator)$')


class ContractWizardResponse(BaseModel):
    """Schema for contract wizard response."""
    status: str
    message: str
    result: Dict[str, Any]


# Flow Automation Schemas
class FlowAutomationRequest(BaseModel):
    """Schema for Flow automation request."""
    contract_content: str = Field(..., min_length=1)
    config_content: Optional[Dict[str, Any]] = None
    contract_name: str = Field("AutoContract", min_length=1)
    network: str = Field("emulator", pattern=r'^(testnet|mainnet|emulator)$')
    auto_deploy: bool = True
    flow_init: bool = True


class FlowAutomationStepResponse(BaseModel):
    """Schema for Flow automation step response."""
    step: str
    status: str
    result: Dict[str, Any]


class FlowAutomationResponse(BaseModel):
    """Schema for Flow automation response."""
    status: str
    steps: List[FlowAutomationStepResponse]
    error: Optional[str] = None


# Dashboard Stats Schema (enhanced)
class DashboardStatsResponse(BaseModel):
    """Schema for dashboard statistics response."""
    total_contracts: int
    successful_deployments: int
    pending_submissions: int
    total_docs: int