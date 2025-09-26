"""
Data models for the Smart Contract LLM Builder.
"""

from .database import Base, get_db, create_tables, drop_tables, check_database_connection
from .user import User, UserDataControl, PersonaType, DataRetentionPreference
from .contract import ContractSubmission, GeneratedConfiguration, InputType, SubmissionStatus, ValidationStatus
from .generated_contract import GeneratedContract, ContractType, NetworkType, GenerationMethod
from .deployment import DeploymentLog, TransactionProposal, DeploymentStatus, TransactionType, ApprovalStatus
from .documentation import DocumentationKnowledgeBase, ContentType
from .learning import LearningFeedbackLoop, PatternType

__all__ = [
    # Database utilities
    "Base",
    "get_db",
    "create_tables",
    "drop_tables",
    "check_database_connection",

    # User models
    "User",
    "UserDataControl",
    "PersonaType",
    "DataRetentionPreference",

    # Contract models
    "ContractSubmission",
    "GeneratedConfiguration",
    "InputType",
    "SubmissionStatus",
    "ValidationStatus",

    # Generated contract models
    "GeneratedContract",
    "ContractType",
    "NetworkType",
    "GenerationMethod",

    # Deployment models
    "DeploymentLog",
    "TransactionProposal",
    "DeploymentStatus",
    "TransactionType",
    "ApprovalStatus",

    # Documentation models
    "DocumentationKnowledgeBase",
    "ContentType",

    # Learning models
    "LearningFeedbackLoop",
    "PatternType",
]