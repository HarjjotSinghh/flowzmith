"""
Model tests for Smart Contract LLM Builder.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from src.models.database import Base
from src.models import (
    User,
    ContractSubmission,
    GeneratedConfiguration,
    DeploymentLog,
    LearningFeedbackLoop,
    DocumentationKnowledgeBase,
    UserDataControl,
    TransactionProposal,
    InputType,
    SubmissionStatus,
    ValidationStatus,
    DeploymentStatus,
    PatternType,
    ContentType,
    PersonaType,
    DataRetentionPeriod
)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_models.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture
def db_session():
    """Create a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

class TestUserModel:
    """Test User model."""

    def test_create_user(self, db_session):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.persona_type == PersonaType.DEVELOPER
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)

    def test_user_relationships(self, db_session):
        """Test user relationships."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user)
        db_session.commit()

        # Create contract submission
        submission = ContractSubmission(
            user_id=user.id,
            input_type=InputType.NATURAL_LANGUAGE,
            content="Create a contract"
        )
        db_session.add(submission)
        db_session.commit()

        # Test relationship
        assert len(user.contract_submissions) == 1
        assert user.contract_submissions[0].content == "Create a contract"

    def test_user_string_representation(self, db_session):
        """Test user string representation."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user)
        db_session.commit()

        assert str(user) == f"<User(id={user.id}, email=test@example.com)>"

class TestContractSubmissionModel:
    """Test ContractSubmission model."""

    def test_create_contract_submission(self, db_session):
        """Test creating a contract submission."""
        # Create user first
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user)
        db_session.commit()

        # Create submission
        submission = ContractSubmission(
            user_id=user.id,
            input_type=InputType.NATURAL_LANGUAGE,
            content="Create a simple NFT contract",
            pre_conditions={"accounts": {"user": "0x123"}},
            post_conditions={"deployed_contracts": ["NFTContract"]},
            status=SubmissionStatus.PENDING
        )
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)

        assert submission.id is not None
        assert submission.user_id == user.id
        assert submission.input_type == InputType.NATURAL_LANGUAGE
        assert submission.status == SubmissionStatus.PENDING
        assert isinstance(submission.created_at, datetime)

    def test_contract_submission_relationships(self, db_session):
        """Test contract submission relationships."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user)
        db_session.commit()

        # Create submission
        submission = ContractSubmission(
            user_id=user.id,
            input_type=InputType.NATURAL_LANGUAGE,
            content="Create a contract"
        )
        db_session.add(submission)
        db_session.commit()

        # Create generated configuration
        config = GeneratedConfiguration(
            submission_id=submission.id,
            config_content={"contracts": {"Test": {}}},
            generated_contract_code="pub contract Test {}",
            validation_status=ValidationStatus.PENDING
        )
        db_session.add(config)
        db_session.commit()

        # Test relationships
        assert submission.generated_config is not None
        assert submission.generated_config.generated_contract_code == "pub contract Test {}"

class TestGeneratedConfigurationModel:
    """Test GeneratedConfiguration model."""

    def test_create_generated_configuration(self, db_session):
        """Test creating a generated configuration."""
        # Create user and submission first
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user)
        db_session.commit()

        submission = ContractSubmission(
            user_id=user.id,
            input_type=InputType.NATURAL_LANGUAGE,
            content="Create a contract"
        )
        db_session.add(submission)
        db_session.commit()

        # Create configuration
        config = GeneratedConfiguration(
            submission_id=submission.id,
            config_content={"contracts": {"Test": {"source": "./Test.cdc"}}},
            generated_contract_code="pub contract Test {}",
            validation_status=ValidationStatus.VALID
        )
        db_session.add(config)
        db_session.commit()
        db_session.refresh(config)

        assert config.id is not None
        assert config.submission_id == submission.id
        assert config.validation_status == ValidationStatus.VALID
        assert isinstance(config.created_at, datetime)

    def test_configuration_relationships(self, db_session):
        """Test configuration relationships."""
        # Create user and submission
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user)
        db_session.commit()

        submission = ContractSubmission(
            user_id=user.id,
            input_type=InputType.NATURAL_LANGUAGE,
            content="Create a contract"
        )
        db_session.add(submission)
        db_session.commit()

        # Create configuration
        config = GeneratedConfiguration(
            submission_id=submission.id,
            config_content={"contracts": {"Test": {}}},
            generated_contract_code="pub contract Test {}"
        )
        db_session.add(config)
        db_session.commit()

        # Create deployment log
        deployment_log = DeploymentLog(
            submission_id=submission.id,
            config_id=config.id,
            network="testnet",
            status=DeploymentStatus.SUCCESS,
            execution_time_ms=1000,
            log_content="Success"
        )
        db_session.add(deployment_log)
        db_session.commit()

        # Test relationships
        assert len(config.deployment_logs) == 1
        assert config.deployment_logs[0].status == DeploymentStatus.SUCCESS

class TestDeploymentLogModel:
    """Test DeploymentLog model."""

    def test_create_deployment_log(self, db_session):
        """Test creating a deployment log."""
        # Create user, submission, and config first
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user)
        db_session.commit()

        submission = ContractSubmission(
            user_id=user.id,
            input_type=InputType.NATURAL_LANGUAGE,
            content="Create a contract"
        )
        db_session.add(submission)
        db_session.commit()

        config = GeneratedConfiguration(
            submission_id=submission.id,
            config_content={"contracts": {"Test": {}}},
            generated_contract_code="pub contract Test {}"
        )
        db_session.add(config)
        db_session.commit()

        # Create deployment log
        deployment_log = DeploymentLog(
            submission_id=submission.id,
            config_id=config.id,
            network="testnet",
            status=DeploymentStatus.SUCCESS,
            transaction_hash="0x123abc",
            gas_used=100,
            execution_time_ms=1000,
            log_content="Deployment successful"
        )
        db_session.add(deployment_log)
        db_session.commit()
        db_session.refresh(deployment_log)

        assert deployment_log.id is not None
        assert deployment_log.network == "testnet"
        assert deployment_log.status == DeploymentStatus.SUCCESS
        assert deployment_log.transaction_hash == "0x123abc"
        assert deployment_log.gas_used == 100

class TestLearningFeedbackLoopModel:
    """Test LearningFeedbackLoop model."""

    def test_create_learning_feedback(self, db_session):
        """Test creating learning feedback."""
        # Create user, submission, and deployment log first
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user)
        db_session.commit()

        submission = ContractSubmission(
            user_id=user.id,
            input_type=InputType.NATURAL_LANGUAGE,
            content="Create a contract"
        )
        db_session.add(submission)
        db_session.commit()

        deployment_log = DeploymentLog(
            submission_id=submission.id,
            config_id="test_config_id",
            network="testnet",
            status=DeploymentStatus.SUCCESS,
            execution_time_ms=1000,
            log_content="Success"
        )
        db_session.add(deployment_log)
        db_session.commit()

        # Create learning feedback
        feedback = LearningFeedbackLoop(
            submission_id=submission.id,
            log_id=deployment_log.id,
            pattern_type=PatternType.SUCCESS_PATTERN,
            insights={"pattern": "successful_deployment"},
            confidence_score=0.9,
            applied_to_generation=False
        )
        db_session.add(feedback)
        db_session.commit()
        db_session.refresh(feedback)

        assert feedback.id is not None
        assert feedback.pattern_type == PatternType.SUCCESS_PATTERN
        assert feedback.confidence_score == 0.9
        assert feedback.applied_to_generation is False

class TestDocumentationKnowledgeBaseModel:
    """Test DocumentationKnowledgeBase model."""

    def test_create_documentation_entry(self, db_session):
        """Test creating documentation entry."""
        doc = DocumentationKnowledgeBase(
            source="OFFICIAL_FLOW_DOCS",
            title="Flow Accounts",
            content_type=ContentType.LANGUAGE_SPEC,
            content="Flow accounts are the foundation...",
            version="1.0.0"
        )
        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)

        assert doc.id is not None
        assert doc.source == "OFFICIAL_FLOW_DOCS"
        assert doc.title == "Flow Accounts"
        assert doc.content_type == ContentType.LANGUAGE_SPEC
        assert isinstance(doc.last_updated, datetime)

class TestUserDataControlModel:
    """Test UserDataControl model."""

    def test_create_user_data_control(self, db_session):
        """Test creating user data control."""
        # Create user first
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user)
        db_session.commit()

        # Create data control
        data_control = UserDataControl(
            user_id=user.id,
            data_retention_period=DataRetentionPeriod.ONE_YEAR,
            allow_learning_data_usage=True,
            allow_analytics_sharing=False,
            marketing_consent=False,
            export_format_preference="JSON"
        )
        db_session.add(data_control)
        db_session.commit()
        db_session.refresh(data_control)

        assert data_control.id is not None
        assert data_control.user_id == user.id
        assert data_control.data_retention_period == DataRetentionPeriod.ONE_YEAR
        assert data_control.allow_learning_data_usage is True

class TestTransactionProposalModel:
    """Test TransactionProposal model."""

    def test_create_transaction_proposal(self, db_session):
        """Test creating transaction proposal."""
        # Create user, submission, and config first
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user)
        db_session.commit()

        submission = ContractSubmission(
            user_id=user.id,
            input_type=InputType.NATURAL_LANGUAGE,
            content="Create a contract"
        )
        db_session.add(submission)
        db_session.commit()

        config = GeneratedConfiguration(
            submission_id=submission.id,
            config_content={"contracts": {"Test": {}}},
            generated_contract_code="pub contract Test {}"
        )
        db_session.add(config)
        db_session.commit()

        # Create transaction proposal
        proposal = TransactionProposal(
            config_id=config.id,
            transaction_type="DEPLOY",
            transaction_data={"contract": "Test"},
            estimated_gas=100,
            user_approval_status="PENDING"
        )
        db_session.add(proposal)
        db_session.commit()
        db_session.refresh(proposal)

        assert proposal.id is not None
        assert proposal.config_id == config.id
        assert proposal.transaction_type == "DEPLOY"
        assert proposal.estimated_gas == 100
        assert proposal.user_approval_status == "PENDING"

class TestModelEnums:
    """Test model enumerations."""

    def test_input_type_enum(self):
        """Test InputType enum."""
        assert InputType.NATURAL_LANGUAGE == "NATURAL_LANGUAGE"
        assert InputType.CDC_FILE == "CDC_FILE"
        assert InputType.SOL_FILE == "SOL_FILE"

    def test_submission_status_enum(self):
        """Test SubmissionStatus enum."""
        assert SubmissionStatus.PENDING == "PENDING"
        assert SubmissionStatus.PROCESSING == "PROCESSING"
        assert SubmissionStatus.COMPLETED == "COMPLETED"
        assert SubmissionStatus.FAILED == "FAILED"

    def test_validation_status_enum(self):
        """Test ValidationStatus enum."""
        assert ValidationStatus.VALID == "VALID"
        assert ValidationStatus.INVALID == "INVALID"
        assert ValidationStatus.PENDING == "PENDING"

    def test_deployment_status_enum(self):
        """Test DeploymentStatus enum."""
        assert DeploymentStatus.SUCCESS == "SUCCESS"
        assert DeploymentStatus.FAILED == "FAILED"
        assert DeploymentStatus.TIMEOUT == "TIMEOUT"
        assert DeploymentStatus.VALIDATION_ERROR == "VALIDATION_ERROR"

    def test_pattern_type_enum(self):
        """Test PatternType enum."""
        assert PatternType.ERROR_PATTERN == "ERROR_PATTERN"
        assert PatternType.SUCCESS_PATTERN == "SUCCESS_PATTERN"
        assert PatternType.OPTIMIZATION_OPPORTUNITY == "OPTIMIZATION_OPPORTUNITY"

    def test_content_type_enum(self):
        """Test ContentType enum."""
        assert ContentType.LANGUAGE_SPEC == "LANGUAGE_SPEC"
        assert ContentType.API_REFERENCE == "API_REFERENCE"
        assert ContentType.TUTORIAL == "TUTORIAL"
        assert ContentType.EXAMPLE == "EXAMPLE"

    def test_persona_type_enum(self):
        """Test PersonaType enum."""
        assert PersonaType.DEVELOPER == "DEVELOPER"
        assert PersonaType.BUSINESS_USER == "BUSINESS_USER"
        assert PersonaType.RESEARCHER == "RESEARCHER"

    def test_data_retention_period_enum(self):
        """Test DataRetentionPeriod enum."""
        assert DataRetentionPeriod.ONE_MONTH == "ONE_MONTH"
        assert DataRetentionPeriod.ONE_YEAR == "ONE_YEAR"
        assert DataRetentionPeriod.INDEFINITE == "INDEFINITE"

class TestModelConstraints:
    """Test model constraints and validations."""

    def test_user_email_constraint(self, db_session):
        """Test user email unique constraint."""
        # Create first user
        user1 = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user1)
        db_session.commit()

        # Try to create user with same email
        user2 = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()

    def test_configuration_unique_submission_constraint(self, db_session):
        """Test configuration unique submission constraint."""
        # Create user and submission
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER
        )
        db_session.add(user)
        db_session.commit()

        submission = ContractSubmission(
            user_id=user.id,
            input_type=InputType.NATURAL_LANGUAGE,
            content="Create a contract"
        )
        db_session.add(submission)
        db_session.commit()

        # Create first configuration
        config1 = GeneratedConfiguration(
            submission_id=submission.id,
            config_content={"contracts": {"Test": {}}},
            generated_contract_code="pub contract Test {}"
        )
        db_session.add(config1)
        db_session.commit()

        # Try to create second configuration for same submission
        config2 = GeneratedConfiguration(
            submission_id=submission.id,
            config_content={"contracts": {"Test2": {}}},
            generated_contract_code="pub contract Test2 {}"
        )
        db_session.add(config2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()

if __name__ == "__main__":
    pytest.main([__file__])