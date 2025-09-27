from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.models.database import Base

class ContractSubmission(Base):
    __tablename__ = "contract_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    generated_contract = Column(Text)
    pre_conditions = Column(JSON)
    post_conditions = Column(JSON)
    network = Column(String, nullable=False)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="contract_submissions")
    deployments = relationship("Deployment", backref="submission")

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("contract_submissions.id"), nullable=False)
    network = Column(String, nullable=False)
    transaction_hash = Column(String)
    contract_address = Column(String)
    status = Column(String, default="PENDING")
    gas_used = Column(Integer)
    error_message = Column(Text)
    config_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ContractConfiguration(Base):
    __tablename__ = "contract_configurations"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("contract_submissions.id"), nullable=False)
    config_type = Column(String, nullable=False)
    configuration = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())