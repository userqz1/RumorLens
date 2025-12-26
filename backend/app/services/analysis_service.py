"""Analysis service for dashboard and statistics."""

import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import Integer, and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.detection import Analysis, Detection
from app.schemas.analysis import (
    CategoryResponse,
    CategoryStats,
    KeywordsResponse,
    KeywordStats,
    OverviewStats,
    RiskDistribution,
    RiskDistributionResponse,
    TrendDataPoint,
    TrendResponse,
)


class AnalysisService:
    """Service for analytics and statistics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview_stats(
        self,
        user_id: uuid.UUID,
    ) -> OverviewStats:
        """Get overview statistics for dashboard."""
        # Total detections
        total_query = select(func.count()).select_from(Detection).where(
            Detection.user_id == user_id
        )
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0

        # Rumors count
        rumors_query = select(func.count()).select_from(Detection).where(
            and_(Detection.user_id == user_id, Detection.is_rumor == True)
        )
        rumors_result = await self.db.execute(rumors_query)
        rumors = rumors_result.scalar() or 0

        # Verified (non-rumors) count
        verified = total - rumors

        # Calculate rumor rate
        rumor_rate = rumors / total if total > 0 else 0.0

        # Average confidence
        avg_query = select(func.avg(Detection.confidence)).where(
            Detection.user_id == user_id
        )
        avg_result = await self.db.execute(avg_query)
        avg_confidence = float(avg_result.scalar() or 0.5)

        return OverviewStats(
            total_detections=total,
            total_rumors=rumors,
            total_verified=verified,
            rumor_rate=rumor_rate,
            avg_confidence=avg_confidence,
        )

    async def get_trend_data(
        self,
        user_id: uuid.UUID,
        days: int = 30,
    ) -> TrendResponse:
        """Get trend data for the specified number of days."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        # Query detections grouped by date
        query = (
            select(
                func.date(Detection.created_at).label("date"),
                func.count().label("total"),
                func.sum(case((Detection.is_rumor == True, 1), else_=0)).label(
                    "rumors"
                ),
            )
            .where(
                and_(
                    Detection.user_id == user_id,
                    Detection.created_at >= start_date,
                    Detection.created_at <= end_date,
                )
            )
            .group_by(func.date(Detection.created_at))
            .order_by(func.date(Detection.created_at))
        )

        result = await self.db.execute(query)
        rows = result.all()

        # Build trend data points
        data_map = {
            str(row.date): TrendDataPoint(
                date=str(row.date),
                total=row.total or 0,
                rumors=row.rumors or 0,
                verified=(row.total or 0) - (row.rumors or 0),
            )
            for row in rows
        }

        # Fill in missing dates
        data = []
        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            if date_str in data_map:
                data.append(data_map[date_str])
            else:
                data.append(
                    TrendDataPoint(date=date_str, total=0, rumors=0, verified=0)
                )
            current += timedelta(days=1)

        return TrendResponse(data=data, period="daily")

    async def get_category_stats(
        self,
        user_id: uuid.UUID,
    ) -> CategoryResponse:
        """Get category distribution statistics."""
        query = (
            select(
                Analysis.category,
                func.count().label("count"),
            )
            .join(Detection, Detection.id == Analysis.detection_id)
            .where(Detection.user_id == user_id)
            .group_by(Analysis.category)
            .order_by(func.count().desc())
        )

        result = await self.db.execute(query)
        rows = result.all()

        total = sum(row.count for row in rows)

        data = [
            CategoryStats(
                category=row.category or "other",
                count=row.count,
                percentage=(row.count / total * 100) if total > 0 else 0,
            )
            for row in rows
        ]

        return CategoryResponse(data=data, total=total)

    async def get_keywords_stats(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
    ) -> KeywordsResponse:
        """Get keyword frequency statistics for word cloud."""
        query = (
            select(Analysis.keywords)
            .join(Detection, Detection.id == Analysis.detection_id)
            .where(Detection.user_id == user_id)
        )

        result = await self.db.execute(query)
        rows = result.all()

        # Count keyword frequencies
        keyword_counter: Counter = Counter()
        for row in rows:
            if row.keywords:
                keyword_counter.update(row.keywords)

        # Get top keywords
        top_keywords = keyword_counter.most_common(limit)
        max_count = top_keywords[0][1] if top_keywords else 1

        data = [
            KeywordStats(
                keyword=keyword,
                count=count,
                weight=count / max_count,
            )
            for keyword, count in top_keywords
        ]

        return KeywordsResponse(
            data=data,
            total_keywords=len(keyword_counter),
        )

    async def get_risk_distribution(
        self,
        user_id: uuid.UUID,
    ) -> RiskDistributionResponse:
        """Get risk level distribution statistics."""
        query = (
            select(
                Detection.risk_level,
                func.count().label("count"),
            )
            .where(Detection.user_id == user_id)
            .group_by(Detection.risk_level)
        )

        result = await self.db.execute(query)
        rows = result.all()

        distribution = RiskDistribution()
        total = 0

        for row in rows:
            count = row.count or 0
            total += count
            if row.risk_level == "low":
                distribution.low = count
            elif row.risk_level == "medium":
                distribution.medium = count
            elif row.risk_level == "high":
                distribution.high = count
            elif row.risk_level == "critical":
                distribution.critical = count

        return RiskDistributionResponse(
            distribution=distribution,
            total=total,
        )
