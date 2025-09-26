"""
Configuration management for Smart Contract LLM Builder.
"""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings

from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    print(os.environ)
    # Application Configuration
    app_name: str = "Smart Contract LLM Builder"
    app_version: str = "1.0.0"
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"), env="DEBUG")
    api_port: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8000")), env="API_PORT")
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"), env="LOG_LEVEL")
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"), env="HOST")
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")), env="PORT")

    # Database Configuration
    database_url: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./smart_contract_llm.db"),
        env="DATABASE_URL"
    )
    vector_db_url: str = Field(
        default_factory=lambda: os.getenv("VECTOR_DB_URL", "chroma:/tmp/chroma_db"),
        env="VECTOR_DB_URL"
    )

    # LLM Provider Configuration
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"), env="OPENAI_API_KEY")
    groq_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GROQ_API_KEY"), env="GROQ_API_KEY")
    # Models (were missing before, map from .env)
    openai_model: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4"), env="OPENAI_MODEL")
    groq_model: Optional[str] = Field(default_factory=lambda: os.getenv("GROQ_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct"), env="GROQ_MODEL")
    # Preferred/default provider selection
    preferred_provider: Optional[str] = Field(default_factory=lambda: os.getenv("PREFERRED_PROVIDER"), env="PREFERRED_PROVIDER")
    default_llm_provider: str = Field(default_factory=lambda: os.getenv("DEFAULT_LLM_PROVIDER", "openai"), env="DEFAULT_LLM_PROVIDER")

    # Flow Blockchain Configuration
    flow_network: str = Field(default_factory=lambda: os.getenv("FLOW_NETWORK", "testnet"), env="FLOW_NETWORK")
    flow_account_address: Optional[str] = Field(default_factory=lambda: os.getenv("FLOW_ACCOUNT_ADDRESS"), env="FLOW_ACCOUNT_ADDRESS")
    flow_private_key: Optional[str] = Field(default_factory=lambda: os.getenv("FLOW_PRIVATE_KEY"), env="FLOW_PRIVATE_KEY")

    # File Processing
    max_file_size: int = Field(default_factory=lambda: int(os.getenv("MAX_FILE_SIZE", "10485760")), env="MAX_FILE_SIZE")  # 10MB
    allowed_file_extensions: List[str] = Field(default_factory=lambda: os.getenv("ALLOWED_FILE_EXTENSIONS", ".cdc,.sol").split(","), env="ALLOWED_FILE_EXTENSIONS")

    # Security & Authentication
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "your-secret-key-change-in-production"), env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")), env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Performance & Scaling
    max_concurrent_requests: int = Field(default_factory=lambda: int(os.getenv("MAX_CONCURRENT_REQUESTS", "100")), env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT", "300")), env="REQUEST_TIMEOUT")  # 5 minutes

    # External Services
    redis_url: str = Field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"), env="REDIS_URL")

    # Documentation & Learning
    enable_analytics: bool = Field(default_factory=lambda: os.getenv("ENABLE_ANALYTICS", "true").lower() in ("true", "1", "yes"), env="ENABLE_ANALYTICS")
    data_retention_days: int = Field(default_factory=lambda: int(os.getenv("DATA_RETENTION_DAYS", "365")), env="DATA_RETENTION_DAYS")

    # File Paths
    flow_projects_path: str = Field(default_factory=lambda: os.getenv("FLOW_PROJECTS_PATH", "./flow_projects"), env="FLOW_PROJECTS_PATH")
    vector_db_path: str = Field(default_factory=lambda: os.getenv("VECTOR_DB_PATH", "./vector_db"), env="VECTOR_DB_PATH")
    log_path: str = Field(default_factory=lambda: os.getenv("LOG_PATH", "./logs"), env="LOG_PATH")

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