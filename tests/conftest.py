"""
Pytest configuration and shared fixtures.
"""

import pytest
import asyncio
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.models.database import Base
from src.models import *
from src.config import get_settings

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_conftest.db"

# Create test engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    pool_pre_ping=True
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password_123",
        persona_type=PersonaType.DEVELOPER,
        full_name="Test User",
        organization="Test Organization",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_submission(db_session: Session, test_user: User) -> ContractSubmission:
    """Create a test contract submission."""
    submission = ContractSubmission(
        user_id=test_user.id,
        input_type=InputType.NATURAL_LANGUAGE,
        content="Create a simple NFT contract with mint and transfer functions",
        pre_conditions={
            "accounts": {"user": "0x123"},
            "tokens": {"initial_supply": 1000}
        },
        post_conditions={
            "deployed_contracts": ["NFTContract"],
            "created_resources": ["NFT"]
        },
        status=SubmissionStatus.PENDING
    )
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    return submission

@pytest.fixture
def test_configuration(db_session: Session, test_submission: ContractSubmission) -> GeneratedConfiguration:
    """Create a test generated configuration."""
    config = GeneratedConfiguration(
        submission_id=test_submission.id,
        config_content={
            "contracts": {
                "NFTContract": {
                    "source": "./NFTContract.cdc",
                    "aliases": {
                        "testnet": "0x456"
                    }
                }
            },
            "networks": {
                "testnet": {
                    "host": "access.devnet.nodes.onflow.org:9000",
                    "chain": "flow-emulator"
                }
            },
            "accounts": {
                "testnet-account": {
                    "address": "0x123",
                    "key": "private-key"
                }
            }
        },
        generated_contract_code="""
            pub contract NFTContract {
                pub var totalSupply: UInt64
                pub let NFTCollection: &NFT.Collection

                pub resource NFT {
                    pub let id: UInt64
                    pub let metadata: {String: String}

                    init(id: UInt64, metadata: {String: String}) {
                        self.id = id
                        self.metadata = metadata
                        NFTContract.totalSupply = NFTContract.totalSupply + 1
                    }

                    destroy() {
                        NFTContract.totalSupply = NFTContract.totalSupply - 1
                    }
                }

                init() {
                    self.totalSupply = 0
                    self.NFTCollection <- create NFT.Collection()
                }

                pub fun mintNFT(metadata: {String: String}): @NFT {
                    let newNFT <- create NFT(id: self.totalSupply, metadata: metadata)
                    return <-newNFT
                }
            }
        """,
        validation_status=ValidationStatus.VALID
    )
    db_session.add(config)
    db_session.commit()
    db_session.refresh(config)
    return config

@pytest.fixture
def test_deployment_log(db_session: Session, test_submission: ContractSubmission, test_configuration: GeneratedConfiguration) -> DeploymentLog:
    """Create a test deployment log."""
    deployment_log = DeploymentLog(
        submission_id=test_submission.id,
        config_id=test_configuration.id,
        deployment_id="deploy_123456",
        network="testnet",
        status=DeploymentStatus.SUCCESS,
        transaction_hash="0xabcdef123456789",
        gas_used=150,
        execution_time_ms=2500,
        log_content="Deployment completed successfully. Transaction ID: 0xabcdef123456789"
    )
    db_session.add(deployment_log)
    db_session.commit()
    db_session.refresh(deployment_log)
    return deployment_log

@pytest.fixture
def test_documentation(db_session: Session) -> DocumentationKnowledgeBase:
    """Create a test documentation entry."""
    doc = DocumentationKnowledgeBase(
        source="OFFICIAL_FLOW_DOCS",
        title="Cadence Resources",
        content_type=ContentType.LANGUAGE_SPEC,
        content="""
            Resources in Cadence are unique types that can only exist in account storage.
            They cannot be copied and must be explicitly moved or destroyed.

            Key characteristics:
            - Resources can only exist in account storage
            - Resources cannot be copied
            - Resources must have explicit destroy() methods
            - Resources can contain other resources
        """,
        version="1.0.0"
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    return doc

@pytest.fixture
def test_user_data_control(db_session: Session, test_user: User) -> UserDataControl:
    """Create a test user data control entry."""
    data_control = UserDataControl(
        user_id=test_user.id,
        data_retention_period=DataRetentionPeriod.ONE_YEAR,
        allow_learning_data_usage=True,
        allow_analytics_sharing=False,
        marketing_consent=False,
        export_format_preference="JSON"
    )
    db_session.add(data_control)
    db_session.commit()
    db_session.refresh(data_control)
    return data_control

@pytest.fixture
def test_learning_feedback(db_session: Session, test_submission: ContractSubmission, test_deployment_log: DeploymentLog) -> LearningFeedbackLoop:
    """Create a test learning feedback entry."""
    feedback = LearningFeedbackLoop(
        submission_id=test_submission.id,
        log_id=test_deployment_log.id,
        pattern_type=PatternType.SUCCESS_PATTERN,
        insights={
            "pattern_type": "deployment_success",
            "elements": [
                {"practice": "proper_resource_definition", "found": True},
                {"practice": "error_handling", "found": True}
            ]
        },
        confidence_score=0.85,
        applied_to_generation=False
    )
    db_session.add(feedback)
    db_session.commit()
    db_session.refresh(feedback)
    return feedback

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "content": "pub contract TestContract {}",
        "tokens_used": 150,
        "cost": 0.015,
        "provider": "OPENAI",
        "model": "gpt-4"
    }

@pytest.fixture
def mock_flow_deployment_result():
    """Mock Flow CLI deployment result."""
    return {
        "status": "SUCCESS",
        "transaction_hash": "0x123456789abcdef",
        "execution_time_ms": 2000,
        "log_content": "Deployment successful"
    }

# Test client fixture
@pytest.fixture
def test_client():
    """Create a test client for FastAPI app."""
    from fastapi.testclient import TestClient
    from src.main import app

    # Override database dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_settings] = lambda: get_settings()
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    yield client

    # Clean up
    app.dependency_overrides.clear()

# Mock settings for testing
@pytest.fixture
def mock_settings():
    """Mock application settings."""
    from src.config import Settings
    return Settings(
        database_url="sqlite:///./test.db",
        openai_api_key="test_key",
        groq_api_key="test_key",
        jwt_secret_key="test_jwt_secret",
        debug=True
    )

# Performance testing fixtures
@pytest.fixture
def performance_test_data(db_session: Session):
    """Create test data for performance testing."""
    users = []
    submissions = []
    configurations = []
    deployments = []

    # Create 10 users
    for i in range(10):
        user = User(
            email=f"perf_user_{i}@example.com",
            password_hash="hashed_password",
            persona_type=PersonaType.DEVELOPER,
            is_active=True
        )
        db_session.add(user)
        users.append(user)

    db_session.commit()

    # Create 50 submissions
    for i, user in enumerate(users):
        for j in range(5):
            submission = ContractSubmission(
                user_id=user.id,
                input_type=InputType.NATURAL_LANGUAGE,
                content=f"Create contract {i}-{j}",
                status=SubmissionStatus.COMPLETED if j % 4 != 0 else SubmissionStatus.FAILED
            )
            db_session.add(submission)
            submissions.append(submission)

    db_session.commit()

    # Create configurations and deployments
    for submission in submissions:
        config = GeneratedConfiguration(
            submission_id=submission.id,
            config_content={"contracts": {"Test": {}}},
            generated_contract_code=f"pub contract Test{submission.id} {{}}",
            validation_status=ValidationStatus.VALID
        )
        db_session.add(config)
        configurations.append(config)

        # Create 2 deployments per submission (one success, one failure)
        for success in [True, False]:
            deployment = DeploymentLog(
                submission_id=submission.id,
                config_id=config.id,
                network="testnet",
                status=DeploymentStatus.SUCCESS if success else DeploymentStatus.FAILED,
                execution_time_ms=1000 + (i * 100),
                log_content="Success" if success else "Failed deployment"
            )
            db_session.add(deployment)
            deployments.append(deployment)

    db_session.commit()

    return {
        "users": users,
        "submissions": submissions,
        "configurations": configurations,
        "deployments": deployments
    }

# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "llm: marks tests that require LLM API access"
    )
    config.addinivalue_line(
        "markers", "flow: marks tests that require Flow CLI access"
    )

# Hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Mark tests that use external services
        if "llm" in item.name.lower() or "openai" in item.name.lower():
            item.add_marker(pytest.mark.llm)
        if "flow" in item.name.lower() or "deployment" in item.name.lower():
            item.add_marker(pytest.mark.flow)

        # Mark slow tests
        if "performance" in item.name.lower() or "integration" in item.name.lower():
            item.add_marker(pytest.mark.slow)

# Skip markers for CI/CD
def pytest_runtest_setup(item):
    """Skip certain tests in CI environment."""
    import os

    if os.environ.get("CI"):
        # Skip LLM tests in CI unless API keys are provided
        if "llm" in item.keywords and not os.environ.get("OPENAI_API_KEY"):
            pytest.skip("Skipping LLM test in CI - no API key provided")

        # Skip Flow tests in CI unless Flow CLI is available
        if "flow" in item.keywords:
            import subprocess
            try:
                subprocess.run(["flow", "version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pytest.skip("Skipping Flow test in CI - Flow CLI not available")