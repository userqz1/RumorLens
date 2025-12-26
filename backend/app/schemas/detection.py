"""Detection schemas for request/response validation."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level enumeration for detection results."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def from_confidence(cls, confidence: float, is_rumor: bool) -> "RiskLevel":
        """Determine risk level based on confidence and rumor status."""
        if not is_rumor:
            return cls.LOW

        # For rumors: lower confidence in being true = higher risk
        if confidence >= 0.8:
            return cls.LOW
        elif confidence >= 0.6:
            return cls.MEDIUM
        elif confidence >= 0.4:
            return cls.HIGH
        else:
            return cls.CRITICAL


class AnalysisResult(BaseModel):
    """Schema for detailed analysis result."""

    keywords: list[str] = Field(default_factory=list)
    sentiment: str = "neutral"
    category: str = "other"
    sources: list[str] = Field(default_factory=list)
    fact_check_points: list[str] = Field(default_factory=list)
    risk_indicators: list[str] = Field(default_factory=list)


class DetectionRequest(BaseModel):
    """Schema for single detection request."""

    content: str = Field(..., min_length=1, max_length=5000)
    include_analysis: bool = True
    include_propagation: bool = False


class DetectionResponse(BaseModel):
    """Schema for detection response."""

    id: uuid.UUID
    content: str
    is_rumor: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    explanation: str
    analysis: Optional[AnalysisResult] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BatchDetectionRequest(BaseModel):
    """Schema for batch detection request."""

    contents: list[str] = Field(..., min_length=1, max_length=100)
    include_analysis: bool = True


class BatchDetectionResponse(BaseModel):
    """Schema for batch detection response."""

    total: int
    success: int
    failed: int
    results: list[DetectionResponse]


class PropagationNode(BaseModel):
    """Schema for propagation node in network visualization."""

    node_id: str
    parent_id: Optional[str] = None
    content: Optional[str] = None
    user_info: Optional[dict] = None
    engagement: Optional[dict] = None
    timestamp: Optional[datetime] = None


class PropagationResponse(BaseModel):
    """Schema for propagation analysis response."""

    detection_id: uuid.UUID
    nodes: list[PropagationNode]
    pattern: Optional[str] = None
    spread_speed: Optional[str] = None
    estimated_reach: Optional[int] = None
    influence_score: Optional[float] = None
