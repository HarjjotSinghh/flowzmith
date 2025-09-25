"""
API schemas for Smart Contract LLM Builder.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

from ..models import (
    InputType,
    SubmissionStatus,
    ValidationStatus,
    DeploymentStatus,
    ApprovalStatus,
    PatternType,
    ContentType,
    PersonaType,
    DataRetentionPreference
)


class UserCreate(BaseModel):
    """Schema for user creation."""
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    organization: Optional[str] = None
    persona_type: PersonaType = PersonaType.EXPERT


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    full_name: Optional[str]
    organization: Optional[str]
    persona_type: PersonaType
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: str
    password: str


class ContractSubmissionCreate(BaseModel):
    """Schema for contract submission creation."""
    input_type: InputType
    content: str = Field(..., min_length=1)
    pre_conditions: Optional[Dict[str, Any]] = None
    post_conditions: Optional[Dict[str, Any]] = None


class ContractSubmissionResponse(BaseModel):
    """Schema for contract submission response."""
    id: UUID
    user_id: UUID
    input_type: InputType
    content: str
    pre_conditions: Optional[Dict[str, Any]]
    post_conditions: Optional[Dict[str, Any]]
    status: SubmissionStatus
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class GeneratedConfigurationResponse(BaseModel):
    """Schema for generated configuration response."""
    id: UUID
    submission_id: UUID
    config_content: Dict[str, Any]
    generated_contract_code: str
    validation_status: ValidationStatus
    validation_errors: Optional[Dict[str, Any]]
    created_at: datetime
    last_modified: datetime

    class Config:
        from_attributes = True


class DeploymentLogResponse(BaseModel):
    """Schema for deployment log response."""
    id: UUID
    submission_id: UUID
    config_id: UUID
    deployment_id: Optional[str]
    network: str
    status: DeploymentStatus
    error_message: Optional[str]
    error_code: Optional[str]
    transaction_hash: Optional[str]
    gas_used: Optional[int]
    execution_time_ms: int
    log_content: str
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionProposalCreate(BaseModel):
    """Schema for transaction proposal creation."""
    config_id: UUID
    transaction_type: str
    transaction_data: Dict[str, Any]


class TransactionProposalResponse(BaseModel):
    """Schema for transaction proposal response."""
    id: UUID
    config_id: UUID
    transaction_type: str
    transaction_data: Dict[str, Any]
    estimated_gas: int
    user_approval_status: ApprovalStatus
    signed_transaction: Optional[str]
    created_at: datetime
    responded_at: Optional[datetime]

    class Config:
        from_attributes = True


class DocumentationSearchRequest(BaseModel):
    """Schema for documentation search request."""
    query: str = Field(..., min_length=1)
    content_type: Optional[ContentType] = None
    limit: int = Field(10, ge=1, le=100)
    use_semantic_search: bool = True


class DocumentationResponse(BaseModel):
    """Schema for documentation response."""
    id: UUID
    source: str
    title: str
    content_type: ContentType
    content: str
    version: Optional[str]
    last_updated: datetime

    class Config:
        from_attributes = True


class LearningFeedbackResponse(BaseModel):
    """Schema for learning feedback response."""
    id: UUID
    submission_id: UUID
    log_id: UUID
    pattern_type: PatternType
    insights: Dict[str, Any]
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    applied_to_generation: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DataControlUpdate(BaseModel):
    """Schema for data control update."""
    data_retention_period: Optional[DataRetentionPreference] = None
    allow_learning_data_usage: Optional[bool] = None
    allow_analytics_sharing: Optional[bool] = None
    marketing_consent: Optional[bool] = None
    export_format_preference: Optional[str] = Field(None, pattern=r'^(JSON|CSV)$')


class DataControlResponse(BaseModel):
    """Schema for data control response."""
    user_id: UUID
    data_retention_period: DataRetentionPreference
    allow_learning_data_usage: bool
    allow_analytics_sharing: bool
    marketing_consent: bool
    export_format_preference: str
    last_updated: datetime

    class Config:
        from_attributes = True


class ExportRequest(BaseModel):
    """Schema for data export request."""
    format_type: str = Field("JSON", pattern=r'^(JSON|CSV)$')


class ExportResponse(BaseModel):
    """Schema for export response."""
    format: str
    data: Any
    exported_at: datetime


class DeleteDataRequest(BaseModel):
    """Schema for data deletion request."""
    data_categories: List[str] = Field(..., min_items=1)


class DeleteDataResponse(BaseModel):
    """Schema for data deletion response."""
    deleted_counts: Dict[str, int]
    deleted_at: datetime


class ContractGenerationRequest(BaseModel):
    """Schema for contract generation request."""
    input_type: InputType
    content: str = Field(..., min_length=1)
    pre_conditions: Optional[Dict[str, Any]] = None
    post_conditions: Optional[Dict[str, Any]] = None
    network: str = Field("testnet", pattern=r'^(testnet|mainnet|emulator)$')


class ContractGenerationResponse(BaseModel):
    """Schema for contract generation response."""
    submission_id: UUID
    config_id: UUID
    generated_contract_code: str
    config_content: Dict[str, Any]
    validation_status: ValidationStatus
    deployment_logs: List[DeploymentLogResponse]

    class Config:
        from_attributes = True


class DeploymentRequest(BaseModel):
    """Schema for deployment request."""
    config_id: UUID
    network: str = Field("testnet", pattern=r'^(testnet|mainnet|emulator)$')


class DeploymentResponse(BaseModel):
    """Schema for deployment response."""
    deployment_id: UUID
    status: DeploymentStatus
    network: str
    transaction_hash: Optional[str]
    gas_used: Optional[int]
    execution_time_ms: int
    log_content: str
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionApprovalRequest(BaseModel):
    """Schema for transaction approval request."""
    approved: bool
    signature: Optional[str] = None


class StatisticsResponse(BaseModel):
    """Schema for statistics response."""
    total_users: int
    active_users: int
    total_submissions: int
    successful_deployments: int
    total_deployments: int
    success_rate: float
    learning_patterns: Dict[str, Any]
    documentation_stats: Dict[str, Any]


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
    llm_providers: List[str]
    flow_cli_available: bool


class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime


class ProgressUpdate(BaseModel):
    """Schema for progress updates."""
    type: str = "progress"
    stage: str
    progress: float = Field(..., ge=0.0, le=1.0)
    message: str
    data: Optional[Dict[str, Any]] = None


class LogUpdate(BaseModel):
    """Schema for log updates."""
    type: str = "log"
    level: str = Field(..., pattern=r'^(INFO|WARNING|ERROR|DEBUG)$')
    message: str
    timestamp: datetime


class StatusUpdate(BaseModel):
    """Schema for status updates."""
    type: str = "status"
    status: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime