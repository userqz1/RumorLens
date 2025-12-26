"""Analysis and statistics API routes."""

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.analysis import (
    CategoryResponse,
    KeywordsResponse,
    OverviewStats,
    RiskDistributionResponse,
    TrendResponse,
)
from app.services.analysis_service import AnalysisService

router = APIRouter()


@router.get("/overview", response_model=OverviewStats)
async def get_overview(
    current_user: CurrentUser,
    db: DbSession,
) -> OverviewStats:
    """Get overview statistics for dashboard."""
    analysis_service = AnalysisService(db)
    return await analysis_service.get_overview_stats(current_user.id)


@router.get("/trend", response_model=TrendResponse)
async def get_trend(
    current_user: CurrentUser,
    db: DbSession,
    days: int = Query(30, ge=1, le=365),
) -> TrendResponse:
    """Get trend data for the specified number of days."""
    analysis_service = AnalysisService(db)
    return await analysis_service.get_trend_data(current_user.id, days)


@router.get("/category", response_model=CategoryResponse)
async def get_category_stats(
    current_user: CurrentUser,
    db: DbSession,
) -> CategoryResponse:
    """Get category distribution statistics."""
    analysis_service = AnalysisService(db)
    return await analysis_service.get_category_stats(current_user.id)


@router.get("/keywords", response_model=KeywordsResponse)
async def get_keywords(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(50, ge=10, le=200),
) -> KeywordsResponse:
    """Get keyword frequency statistics for word cloud."""
    analysis_service = AnalysisService(db)
    return await analysis_service.get_keywords_stats(current_user.id, limit)


@router.get("/risk-distribution", response_model=RiskDistributionResponse)
async def get_risk_distribution(
    current_user: CurrentUser,
    db: DbSession,
) -> RiskDistributionResponse:
    """Get risk level distribution statistics."""
    analysis_service = AnalysisService(db)
    return await analysis_service.get_risk_distribution(current_user.id)
