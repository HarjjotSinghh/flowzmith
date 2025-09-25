"""
Learning and feedback-related data models.
"""

from sqlalchemy import Column, String, DateTime, JSON, Text, Float, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum
import uuid


class PatternType(str, enum.Enum):
    """Pattern types for learning feedback."""
    ERROR_PATTERN = "ERROR_PATTERN"
    SUCCESS_PATTERN = "SUCCESS_PATTERN"
    OPTIMIZATION_OPPORTUNITY = "OPTIMIZATION_OPPORTUNITY"


class LearningFeedbackLoop(Base):
    """System that analyzes deployment logs to improve contract generation."""

    __tablename__ = "learning_feedback_loops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("contract_submissions.id"), nullable=False)
    log_id = Column(UUID(as_uuid=True), ForeignKey("deployment_logs.id"), nullable=False)
    pattern_type = Column(Enum(PatternType), nullable=False)
    insights = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0-1.0
    applied_to_generation = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    contract_submission = relationship("ContractSubmission")
    deployment_log = relationship("DeploymentLog")

    def __repr__(self):
        return f"<LearningFeedbackLoop(id={self.id}, pattern_type={self.pattern_type}, confidence={self.confidence_score})>"