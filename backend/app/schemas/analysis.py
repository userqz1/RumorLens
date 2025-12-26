"""Analysis schemas for dashboard and statistics."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OverviewStats(BaseModel):
    """Schema for dashboard overview statistics."""

    total_detections: int = 0
    total_rumors: int = 0
    total_verified: int = 0
    rumor_rate: float = Field(0.0, ge=0.0, le=1.0)
    avg_confidence: float = Field(0.0, ge=0.0, le=1.0)


class TrendDataPoint(BaseModel):
    """Schema for trend chart data point."""

    date: str
    rumors: int = 0
    verified: int = 0
    total: int = 0


class TrendResponse(BaseModel):
    """Schema for trend analysis response."""

    data: list[TrendDataPoint]
    period: str = "daily"


class CategoryStats(BaseModel):
    """Schema for category statistics."""

    category: str
    count: int
    percentage: float = Field(0.0, ge=0.0, le=100.0)


class CategoryResponse(BaseModel):
    """Schema for category distribution response."""

    data: list[CategoryStats]
    total: int


class KeywordStats(BaseModel):
    """Schema for keyword statistics."""

    keyword: str
    count: int
    weight: float = Field(1.0, ge=0.0)


class KeywordsResponse(BaseModel):
    """Schema for keywords/word cloud response."""

    data: list[KeywordStats]
    total_keywords: int


class RiskDistribution(BaseModel):
    """Schema for risk level distribution."""

    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


class RiskDistributionResponse(BaseModel):
    """Schema for risk distribution response."""

    distribution: RiskDistribution
    total: int


class HistoryFilter(BaseModel):
    """Schema for history filtering options."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_rumor: Optional[bool] = None
    risk_level: Optional[str] = None
    category: Optional[str] = None
    keyword: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class HistoryStats(BaseModel):
    """Schema for history statistics."""

    total_records: int
    rumors_count: int
    verified_count: int
    by_risk_level: RiskDistribution
