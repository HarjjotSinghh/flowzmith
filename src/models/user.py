"""
User-related data models.
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum
import uuid


class PersonaType(str, enum.Enum):
    """User persona types."""
    EXPERT = "EXPERT"
    INTERMEDIATE = "INTERMEDIATE"
    BEGINNER = "BEGINNER"
    NON_TECHNICAL = "NON_TECHNICAL"


class DataRetentionPreference(str, enum.Enum):
    """Data retention preferences."""
    KEEP_ALL = "KEEP_ALL"
    DELETE_AFTER_30D = "DELETE_AFTER_30D"
    DELETE_IMMEDIATELY = "DELETE_IMMEDIATELY"


class User(Base):
    """System user with different persona types and access levels."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    persona_type = Column(Enum(PersonaType), nullable=False)
    flow_account_address = Column(String(255), nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    preferences = Column(JSON, nullable=True)
    data_retention_consent = Column(Boolean, default=False)

    # Relationships
    contract_submissions = relationship("ContractSubmission", back_populates="user", cascade="all, delete-orphan")
    data_control = relationship("UserDataControl", back_populates="user", uselist=False)
    cli_logs = relationship("CLILog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, persona_type={self.persona_type})>"


class UserDataControl(Base):
    """User preferences and controls for data retention and deletion."""

    __tablename__ = "user_data_controls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    data_retention_preference = Column(Enum(DataRetentionPreference), default=DataRetentionPreference.KEEP_ALL)
    learning_consent = Column(Boolean, default=False)
    deletion_requests = Column(JSON, nullable=True)
    last_data_access = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="data_control")

    def __repr__(self):
        return f"<UserDataControl(user_id={self.user_id}, retention_preference={self.data_retention_preference})>"