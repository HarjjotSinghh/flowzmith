from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.database import Base
from datetime import datetime, timezone
import uuid
from enum import Enum as PyEnum

class CLILogStatus(PyEnum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    PENDING = "PENDING"  # Add PENDING if needed

class CLILog(Base):
    __tablename__ = "cli_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    command = Column(String(500), nullable=False)
    full_output = Column(Text, nullable=False)
    extracted_data = Column(JSON, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    status = Column(Enum(CLILogStatus), default=CLILogStatus.PENDING, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    contract_submission_id = Column(UUID(as_uuid=True), ForeignKey("contract_submissions.id"), nullable=True)

    # String-based relationships to avoid circular imports
    user = relationship("User", back_populates="cli_logs")
    contract_submission = relationship("ContractSubmission", back_populates="cli_logs")

    def update_end_time(self):
        if self.start_time:
            self.end_time = datetime.now(timezone.utc)
            self.duration_ms = int((self.end_time - self.start_time).total_seconds() * 1000)

    def __repr__(self):
        return f"<CLILog(id={self.id}, command={self.command[:50]}..., status={self.status})>"
