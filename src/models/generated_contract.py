"""
Generated contract data models for CLI-generated contracts.
"""

from sqlalchemy import Column, String, DateTime, JSON, Text, Enum, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .database import Base
import enum
import uuid


class ContractType(str, enum.Enum):
    """Contract types."""
    TOKEN = "TOKEN"
    NFT = "NFT"
    DEFI = "DEFI"
    MARKETPLACE = "MARKETPLACE"
    GOVERNANCE = "GOVERNANCE"
    UTILITY = "UTILITY"
    CUSTOM = "CUSTOM"


class NetworkType(str, enum.Enum):
    """Network types."""
    MAINNET = "MAINNET"
    TESTNET = "TESTNET"
    EMULATOR = "EMULATOR"


class GenerationMethod(str, enum.Enum):
    """Contract generation methods."""
    AI_ASSISTED = "AI_ASSISTED"
    TEMPLATE_BASED = "TEMPLATE_BASED"
    MANUAL = "MANUAL"


class GeneratedContract(Base):
    """Represents a contract generated through the CLI tool."""

    __tablename__ = "generated_contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Contract metadata
    name = Column(String(255), nullable=False)
    contract_type = Column(Enum(ContractType), nullable=False)
    description = Column(Text, nullable=True)
    network = Column(Enum(NetworkType), nullable=False)
    
    # Generation details
    generation_method = Column(Enum(GenerationMethod), default=GenerationMethod.AI_ASSISTED)
    requirements_text = Column(Text, nullable=True)  # Original user requirements
    context_used = Column(JSON, nullable=True)  # Context files used for generation
    
    # Contract content
    contract_code = Column(Text, nullable=False)
    
    # File system details
    project_directory = Column(String(500), nullable=False)  # Path to flow_projects directory
    contract_file_path = Column(String(500), nullable=False)  # Path to .cdc file
    
    # Additional Flow project files
    has_transactions = Column(Boolean, default=False)
    has_scripts = Column(Boolean, default=False)
    has_tests = Column(Boolean, default=False)
    flow_json_config = Column(JSON, nullable=True)  # flow.json configuration
    
    # Token/NFT specific metadata (if applicable)
    token_metadata = Column(JSON, nullable=True)  # Token name, symbol, supply, etc.
    
    # Features and capabilities
    features = Column(JSON, nullable=True)  # List of features implemented
    
    # Generation statistics
    context_files_count = Column(Integer, default=0)
    context_size_chars = Column(Integer, default=0)
    generation_time_seconds = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_modified = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<GeneratedContract(id={self.id}, name={self.name}, type={self.contract_type})>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': str(self.id),
            'name': self.name,
            'contract_type': self.contract_type.value if self.contract_type else None,
            'description': self.description,
            'network': self.network.value if self.network else None,
            'generation_method': self.generation_method.value if self.generation_method else None,
            'requirements_text': self.requirements_text,
            'context_used': self.context_used,
            'project_directory': self.project_directory,
            'contract_file_path': self.contract_file_path,
            'has_transactions': self.has_transactions,
            'has_scripts': self.has_scripts,
            'has_tests': self.has_tests,
            'flow_json_config': self.flow_json_config,
            'token_metadata': self.token_metadata,
            'features': self.features,
            'context_files_count': self.context_files_count,
            'context_size_chars': self.context_size_chars,
            'generation_time_seconds': self.generation_time_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None
        }