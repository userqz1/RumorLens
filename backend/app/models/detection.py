"""Detection and analysis database models."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Detection(Base):
    """Detection record model for storing rumor detection results."""

    __tablename__ = "detections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    is_rumor: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    confidence: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
    )
    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    explanation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    raw_response: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="detections",
    )
    analysis: Mapped[Optional["Analysis"]] = relationship(
        "Analysis",
        back_populates="detection",
        uselist=False,
        cascade="all, delete-orphan",
    )
    propagation_nodes: Mapped[list["PropagationNode"]] = relationship(
        "PropagationNode",
        back_populates="detection",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Detection(id={self.id}, is_rumor={self.is_rumor})>"


class Analysis(Base):
    """Analysis result model for detailed rumor analysis."""

    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    detection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("detections.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    keywords: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )
    sentiment: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    sources: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )
    fact_check_points: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    detection: Mapped["Detection"] = relationship(
        "Detection",
        back_populates="analysis",
    )

    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, detection_id={self.detection_id})>"


class PropagationNode(Base):
    """Propagation node model for tracking rumor spread paths."""

    __tablename__ = "propagation_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    detection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("detections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    user_info: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    engagement: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    detection: Mapped["Detection"] = relationship(
        "Detection",
        back_populates="propagation_nodes",
    )

    def __repr__(self) -> str:
        return f"<PropagationNode(id={self.id}, node_id={self.node_id})>"
