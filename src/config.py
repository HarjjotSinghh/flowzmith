"""
Configuration management for Smart Contract LLM Builder.
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application Configuration
    app_name: str = "Smart Contract LLM Builder"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    api_port: int = Field(default=8000, env="API_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./smart_contract_llm.db",
        env="DATABASE_URL"
    )
    vector_db_url: str = Field(
        default="chroma:/tmp/chroma_db",
        env="VECTOR_DB_URL"
    )

    # LLM Provider Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    default_llm_provider: str = Field(default="openai", env="DEFAULT_LLM_PROVIDER")

    # Flow Blockchain Configuration
    flow_network: str = Field(default="testnet", env="FLOW_NETWORK")
    flow_account_address: Optional[str] = Field(default=None, env="FLOW_ACCOUNT_ADDRESS")
    flow_private_key: Optional[str] = Field(default=None, env="FLOW_PRIVATE_KEY")

    # File Processing
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_extensions: List[str] = Field(default=[".cdc", ".sol"])

    # Security & Authentication
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Performance & Scaling
    max_concurrent_requests: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=300, env="REQUEST_TIMEOUT")  # 5 minutes

    # External Services
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # Documentation & Learning
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")
    data_retention_days: int = Field(default=365, env="DATA_RETENTION_DAYS")

    # File Paths
    flow_projects_path: str = Field(default="./flow_projects", env="FLOW_PROJECTS_PATH")
    vector_db_path: str = Field(default="./vector_db", env="VECTOR_DB_PATH")
    log_path: str = Field(default="./logs", env="LOG_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings


def get_database_url() -> str:
    """Get appropriate database URL based on environment."""
    if settings.debug and settings.database_url.startswith("sqlite"):
        return settings.database_url
    return settings.database_url


def get_vector_db_config() -> dict:
    """Get vector database configuration."""
    if settings.vector_db_url.startswith("chroma"):
        return {
            "type": "chroma",
            "path": settings.vector_db_url.replace("chroma:", ""),
            "persist_directory": "./chroma_db"
        }
    elif settings.vector_db_url.startswith("postgres"):
        return {
            "type": "postgres",
            "connection_string": settings.vector_db_url
        }
    else:
        raise ValueError(f"Unsupported vector database type: {settings.vector_db_url}")


def validate_settings() -> List[str]:
    """Validate critical settings and return list of warnings/errors."""
    warnings = []

    # Check for required API keys
    if not settings.openai_api_key and not settings.groq_api_key:
        warnings.append("No LLM API keys configured. Set OPENAI_API_KEY or GROQ_API_KEY")

    # Check Flow configuration for production
    if not settings.debug:
        if not settings.flow_account_address:
            warnings.append("Flow account address not configured for production")
        if not settings.flow_private_key:
            warnings.append("Flow private key not configured for production")

    # Check database configuration
    if settings.database_url.startswith("sqlite") and not settings.debug:
        warnings.append("Using SQLite in production is not recommended")

    return warnings