"""
Database models for InsightProfile application.
Defines tables for storing Humantic profiles and Gemini analyses.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base


class HumanticProfile(Base):
    """
    Stores Humantic AI profile data for caching purposes.
    
    Table stores:
    - LinkedIn URL (unique index for fast lookups)
    - Humantic user_id
    - Full profile data from Humantic API
    - Extracted Big Five personality scores
    - Timestamps for creation and updates
    """
    __tablename__ = "humantic_profiles"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    
    # LinkedIn URL - unique constraint for deduplication
    linkedin_url = Column(
        String(512),
        unique=True,
        nullable=False,
        index=True  # Index for fast lookups
    )
    
    # Humantic user ID returned by their API
    user_id = Column(
        String(256),
        nullable=False,
        index=True
    )
    
    # Full profile data from Humantic API (stored as JSONB for querying)
    profile_data = Column(
        JSON,
        nullable=False
    )
    
    # Extracted Big Five personality scores (0-100 range)
    big_five_scores = Column(
        JSON,
        nullable=True
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationship to Gemini analyses
    gemini_analyses = relationship(
        "GeminiAnalysis",
        back_populates="humantic_profile",
        cascade="all, delete-orphan"
    )
    
    # Create composite index for common queries
    __table_args__ = (
        Index('idx_linkedin_url_created', 'linkedin_url', 'created_at'),
    )
    
    def __repr__(self):
        return f"<HumanticProfile(id={self.id}, linkedin_url={self.linkedin_url[:50]}...)>"


class GeminiAnalysis(Base):
    """
    Stores Gemini AI analysis results linked to Humantic profiles.
    
    Table stores:
    - Reference to parent Humantic profile
    - Summary text from Gemini
    - Strengths and weaknesses arrays
    - Full raw response from Gemini
    - Timestamps
    """
    __tablename__ = "gemini_analyses"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    
    # Foreign key to HumanticProfile
    humantic_profile_id = Column(
        UUID(as_uuid=True),
        ForeignKey('humantic_profiles.id', ondelete='CASCADE'),
        nullable=False,
        index=True  # Index for fast joins
    )
    
    # Summary text (2-sentence personality summary)
    summary = Column(
        Text,
        nullable=False
    )
    
    # Strengths array (stored as JSON array)
    strengths = Column(
        JSON,
        nullable=False
    )
    
    # Weaknesses array (stored as JSON array)
    weaknesses = Column(
        JSON,
        nullable=False
    )
    
    # Full raw response from Gemini (for debugging/auditing)
    raw_response = Column(
        JSON,
        nullable=True
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationship to HumanticProfile
    humantic_profile = relationship(
        "HumanticProfile",
        back_populates="gemini_analyses"
    )
    
    def __repr__(self):
        return f"<GeminiAnalysis(id={self.id}, profile_id={self.humantic_profile_id})>"
