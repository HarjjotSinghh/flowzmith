"""
Documentation-related data models.
"""

from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum
import uuid


class ContentType(str, enum.Enum):
    """Documentation content types."""
    LANGUAGE_SPEC = "LANGUAGE_SPEC"
    API_REFERENCE = "API_REFERENCE"
    TUTORIAL = "TUTORIAL"
    EXAMPLE = "EXAMPLE"
    CODE_EXAMPLE = "CODE_EXAMPLE"


class DocumentationKnowledgeBase(Base):
    """Indexed Flow blockchain and Cadence documentation."""

    __tablename__ = "documentation_knowledge_base"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(1000), nullable=False)
    title = Column(String(500), nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    content = Column(Text, nullable=False)
    embedding_vector = Column(JSON)  # Vector representation for semantic search (stored as JSON for SQLite compatibility)
    chunk_index = Column(Integer, nullable=True)  # Chunk index for large documents
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    version = Column(String(50), nullable=True)

    # No direct relationships - standalone entity for search

    def __repr__(self):
        return f"<DocumentationKnowledgeBase(id={self.id}, title={self.title}, type={self.content_type})>"