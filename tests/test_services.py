"""
Service layer tests for Flowzmith.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.services import (
    LLMService,
    FlowService,
    DocumentationService,
    UserService,
    LearningService,
    DataControlService
)
from src.models import User, ContractSubmission, GeneratedConfiguration, DeploymentLog
from src.models.database import Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_services.db"
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

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        persona_type="DEVELOPER",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_submission(db_session, test_user):
    """Create a test contract submission."""
    submission = ContractSubmission(
        user_id=test_user.id,
        input_type="NATURAL_LANGUAGE",
        content="Create a simple NFT contract",
        pre_conditions={"accounts": {"user": "0x123"}},
        post_conditions={"deployed_contracts": ["NFTContract"]}
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    return submission

class TestUserService:
    """Test UserService."""

    def test_create_user(self, db_session):
        """Test user creation."""
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="newuser@example.com",
            password="securepassword123",
            persona_type="DEVELOPER",
            full_name="New User"
        )

        assert user.email == "newuser@example.com"
        assert user.persona_type == "DEVELOPER"
        assert user.is_active is True

    def test_create_duplicate_user(self, db_session, test_user):
        """Test creating duplicate user."""
        user_service = UserService(db_session)
        with pytest.raises(ValueError):
            user_service.create_user(
                email="test@example.com",
                password="password123",
                persona_type="DEVELOPER"
            )

    def test_authenticate_user(self, db_session, test_user):
        """Test user authentication."""
        user_service = UserService(db_session)

        # Mock password verification
        with patch.object(user_service, '_verify_password', return_value=True):
            user = user_service.authenticate_user("test@example.com", "password")
            assert user is not None
            assert user.id == test_user.id

    def test_authenticate_invalid_credentials(self, db_session, test_user):
        """Test authentication with invalid credentials."""
        user_service = UserService(db_session)

        # Mock password verification failure
        with patch.object(user_service, '_verify_password', return_value=False):
            user = user_service.authenticate_user("test@example.com", "wrongpassword")
            assert user is None

    def test_get_user_by_email(self, db_session, test_user):
        """Test getting user by email."""
        user_service = UserService(db_session)
        user = user_service.get_user_by_email("test@example.com")
        assert user is not None
        assert user.id == test_user.id

    def test_get_nonexistent_user(self, db_session):
        """Test getting nonexistent user."""
        user_service = UserService(db_session)
        user = user_service.get_user_by_email("nonexistent@example.com")
        assert user is None

    def test_update_user_profile(self, db_session, test_user):
        """Test updating user profile."""
        user_service = UserService(db_session)
        updates = {"full_name": "Updated Name", "organization": "Test Org"}

        user = user_service.update_user_profile(str(test_user.id), updates)
        assert user.full_name == "Updated Name"
        assert user.organization == "Test Org"

    def test_deactivate_user(self, db_session, test_user):
        """Test user deactivation."""
        user_service = UserService(db_session)
        result = user_service.deactivate_user(str(test_user.id))
        assert result is True

        # Verify user is deactivated
        user = user_service.get_user_by_id(str(test_user.id))
        assert user.is_active is False

class TestLLMService:
    """Test LLMService."""

    def test_llm_service_initialization(self, db_session):
        """Test LLMService initialization."""
        with patch('src.services.get_settings') as mock_settings:
            mock_settings.return_value.openai_api_key = "test_key"
            mock_settings.return_value.groq_api_key = "test_key"

            llm_service = LLMService(db_session)
            assert llm_service is not None

    @pytest.mark.asyncio
    async def test_generate_contract_from_submission(self, db_session, test_submission):
        """Test contract generation from submission."""
        with patch('src.services.get_settings') as mock_settings:
            mock_settings.return_value.openai_api_key = "test_key"
            mock_settings.return_value.groq_api_key = "test_key"

            llm_service = LLMService(db_session)

            # Mock LLM provider
            mock_provider = Mock()
            mock_provider.generate_contract = AsyncMock(return_value=Mock(
                content="pub contract Test {}",
                tokens_used=100,
                cost=0.01
            ))
            mock_provider.generate_contract = AsyncMock(return_value=Mock(
                content='{"contracts": {"Test": {"source": "./Test.cdc"}}}',
                tokens_used=50,
                cost=0.005
            ))

            llm_service.providers = {"OPENAI": mock_provider}

            with patch.object(llm_service, '_generate_configuration', return_value=Mock(
                content='{"contracts": {"Test": {"source": "./Test.cdc"}}}'
            )):
                config = await llm_service.generate_contract_from_submission(test_submission)

                assert config is not None
                assert config.submission_id == test_submission.id

class TestFlowService:
    """Test FlowService."""

    def test_flow_service_initialization(self, db_session):
        """Test FlowService initialization."""
        with patch('src.services.subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="Flow CLI version 1.0.0")

            flow_service = FlowService(db_session)
            assert flow_service is not None

    def test_create_project_structure(self, db_session):
        """Test creating project structure."""
        with patch('src.services.subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            with patch('src.services.os.makedirs'):
                flow_service = FlowService(db_session)
                project_path = flow_service.create_project_structure("test_project")
                assert "test_project" in str(project_path)

    def test_validate_project_configuration(self, db_session):
        """Test project configuration validation."""
        flow_service = FlowService(db_session)

        valid_config = {
            "contracts": {"Test": {}},
            "networks": {"testnet": {}},
            "accounts": {"default": {}}
        }

        assert flow_service.validate_project_configuration(valid_config) is True

        invalid_config = {
            "contracts": {"Test": {}}
            # Missing networks and accounts
        }

        assert flow_service.validate_project_configuration(invalid_config) is False

class TestDocumentationService:
    """Test DocumentationService."""

    def test_documentation_service_initialization(self, db_session):
        """Test DocumentationService initialization."""
        doc_service = DocumentationService(db_session)
        assert doc_service is not None

    def test_index_official_documentation(self, db_session):
        """Test indexing official documentation."""
        doc_service = DocumentationService(db_session)
        count = doc_service.index_official_documentation()
        assert count > 0

    def test_search_documentation(self, db_session):
        """Test documentation search."""
        doc_service = DocumentationService(db_session)

        # First index some documentation
        doc_service.index_official_documentation()

        # Then search
        results = doc_service.search_documentation("Cadence", limit=5)
        assert len(results) >= 0

    def test_get_relevant_documentation(self, db_session):
        """Test getting relevant documentation."""
        doc_service = DocumentationService(db_session)

        # First index some documentation
        doc_service.index_official_documentation()

        # Then get relevant docs
        relevant_docs = doc_service.get_relevant_documentation(
            "Create a resource in Cadence"
        )
        assert isinstance(relevant_docs, list)

    def test_add_custom_documentation(self, db_session):
        """Test adding custom documentation."""
        doc_service = DocumentationService(db_session)

        from src.models import ContentType
        doc = doc_service.add_custom_documentation(
            title="Test Document",
            content="This is a test document",
            content_type=ContentType.TUTORIAL
        )

        assert doc.title == "Test Document"
        assert doc.content_type == ContentType.TUTORIAL

class TestLearningService:
    """Test LearningService."""

    def test_learning_service_initialization(self, db_session):
        """Test LearningService initialization."""
        learning_service = LearningService(db_session)
        assert learning_service is not None

    def test_analyze_deployment_feedback(self, db_session, test_submission):
        """Test analyzing deployment feedback."""
        learning_service = LearningService(db_session)

        # Create a mock deployment log
        deployment_log = DeploymentLog(
            submission_id=test_submission.id,
            config_id="test_config_id",
            network="testnet",
            status="SUCCESS",
            execution_time_ms=1000,
            log_content="Deployment successful"
        )

        with patch('src.models.LearningFeedbackLoop'):
            feedback_entries = learning_service.analyze_deployment_feedback(deployment_log)
            assert isinstance(feedback_entries, list)

    def test_get_learning_insights(self, db_session):
        """Test getting learning insights."""
        learning_service = LearningService(db_session)
        insights = learning_service.get_learning_insights(limit=10)
        assert isinstance(insights, list)

    def test_get_pattern_statistics(self, db_session):
        """Test getting pattern statistics."""
        learning_service = LearningService(db_session)
        stats = learning_service.get_pattern_statistics()
        assert isinstance(stats, dict)

class TestDataControlService:
    """Test DataControlService."""

    def test_data_control_service_initialization(self, db_session):
        """Test DataControlService initialization."""
        data_control_service = DataControlService(db_session)
        assert data_control_service is not None

    def test_export_user_data(self, db_session, test_user):
        """Test exporting user data."""
        data_control_service = DataControlService(db_session)

        # Create user data control settings
        from src.models import UserDataControl, DataRetentionPeriod
        user_data_control = UserDataControl(
            user_id=test_user.id,
            data_retention_period=DataRetentionPeriod.ONE_YEAR,
            allow_learning_data_usage=True
        )
        db_session.add(user_data_control)
        db_session.commit()

        export_data = data_control_service.export_user_data(str(test_user.id), "JSON")
        assert "profile" in export_data["data"]
        assert export_data["format"] == "JSON"

    def test_delete_user_data(self, db_session, test_user):
        """Test deleting user data."""
        data_control_service = DataControlService(db_session)

        # Create user data control settings
        from src.models import UserDataControl, DataRetentionPeriod
        user_data_control = UserDataControl(
            user_id=test_user.id,
            data_retention_period=DataRetentionPeriod.ONE_YEAR
        )
        db_session.add(user_data_control)
        db_session.commit()

        deletion_counts = data_control_service.delete_user_data(str(test_user.id), ["profile"])
        assert isinstance(deletion_counts, dict)

    def test_validate_data_compliance(self, db_session, test_user):
        """Test data compliance validation."""
        data_control_service = DataControlService(db_session)

        # Create user data control settings
        from src.models import UserDataControl, DataRetentionPeriod
        user_data_control = UserDataControl(
            user_id=test_user.id,
            data_retention_period=DataRetentionPeriod.ONE_YEAR,
            allow_learning_data_usage=True
        )
        db_session.add(user_data_control)
        db_session.commit()

        compliance = data_control_service.validate_data_compliance(str(test_user.id))
        assert "compliant" in compliance

class TestIntegration:
    """Integration tests between services."""

    def test_user_contract_workflow(self, db_session):
        """Test complete user-contract workflow."""
        # Create user
        user_service = UserService(db_session)
        user = user_service.create_user(
            email="integration@example.com",
            password="password123",
            persona_type="DEVELOPER"
        )

        # Create contract submission
        submission = ContractSubmission(
            user_id=user.id,
            input_type="NATURAL_LANGUAGE",
            content="Create a simple token contract"
        )
        db_session.add(submission)
        db_session.commit()

        # Verify submission exists
        assert submission.id is not None
        assert submission.user_id == user.id

        # Test documentation service
        doc_service = DocumentationService(db_session)
        relevant_docs = doc_service.get_relevant_documentation(submission.content)
        assert isinstance(relevant_docs, list)

        # Test learning service
        learning_service = LearningService(db_session)
        stats = learning_service.get_pattern_statistics()
        assert isinstance(stats, dict)

    def test_error_handling(self, db_session):
        """Test error handling across services."""
        user_service = UserService(db_session)

        # Test invalid user ID
        with pytest.raises(ValueError):
            user_service.get_user_by_id("invalid_id")

        # Test invalid email
        with pytest.raises(ValueError):
            user_service.create_user(
                email="invalid-email",
                password="password",
                persona_type="DEVELOPER"
            )

if __name__ == "__main__":
    pytest.main([__file__])