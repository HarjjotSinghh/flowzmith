"""
Deployment-related data models.
"""

from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum
import uuid


class DeploymentStatus(str, enum.Enum):
    """Deployment status."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    VALIDATION_ERROR = "VALIDATION_ERROR"


class TransactionType(str, enum.Enum):
    """Transaction types."""
    DEPLOY = "DEPLOY"
    UPDATE = "UPDATE"
    INTERACT = "INTERACT"


class ApprovalStatus(str, enum.Enum):
    """Transaction approval status."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class DeploymentLog(Base):
    """Structured record of contract deployment attempts and results."""

    __tablename__ = "deployment_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("contract_submissions.id"), nullable=False)
    config_id = Column(UUID(as_uuid=True), ForeignKey("generated_configurations.id"), nullable=False)
    deployment_id = Column(String(255), nullable=True)
    network = Column(String(50), nullable=False)
    status = Column(Enum(DeploymentStatus), nullable=False)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)
    transaction_hash = Column(String(255), nullable=True)
    gas_used = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=False)
    log_content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    contract_submission = relationship("ContractSubmission", back_populates="deployment_logs")
    generated_configuration = relationship("GeneratedConfiguration", back_populates="deployment_logs")

    def __repr__(self):
        return f"<DeploymentLog(id={self.id}, status={self.status}, network={self.network})>"


class TransactionProposal(Base):
    """System-generated transaction suggestions for user approval."""

    __tablename__ = "transaction_proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_id = Column(UUID(as_uuid=True), ForeignKey("generated_configurations.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    transaction_data = Column(JSON, nullable=False)
    estimated_gas = Column(Integer, nullable=False)
    user_approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    signed_transaction = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    generated_configuration = relationship("GeneratedConfiguration", back_populates="transaction_proposals")

    def __repr__(self):
        return f"<TransactionProposal(id={self.id}, type={self.transaction_type}, status={self.user_approval_status})>"