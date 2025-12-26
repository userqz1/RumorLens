"""Detection service for rumor detection operations."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.detection import Analysis, Detection
from app.schemas.detection import (
    AnalysisResult,
    DetectionRequest,
    DetectionResponse,
    RiskLevel,
)
from app.services.deepseek_service import DeepSeekService


class DetectionService:
    """Service for rumor detection operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.deepseek = DeepSeekService()

    async def detect_single(
        self,
        user_id: uuid.UUID,
        request: DetectionRequest,
    ) -> Detection:
        """
        Perform single text detection.

        Args:
            user_id: The user performing the detection
            request: Detection request with content

        Returns:
            Detection record with results
        """
        # Call DeepSeek API
        result = await self.deepseek.detect_rumor(request.content)

        # Determine risk level
        risk_level = RiskLevel.from_confidence(
            result["confidence"],
            result["is_rumor"],
        )

        # Create detection record
        detection = Detection(
            user_id=user_id,
            content=request.content,
            is_rumor=result["is_rumor"],
            confidence=result["confidence"],
            risk_level=risk_level.value,
            explanation=result["explanation"],
            raw_response=result,
        )
        self.db.add(detection)
        await self.db.flush()

        # Create analysis record if requested
        if request.include_analysis:
            analysis = Analysis(
                detection_id=detection.id,
                keywords=result.get("keywords", []),
                sentiment=result.get("sentiment", "neutral"),
                category=result.get("category", "other"),
                sources=result.get("sources", []),
                fact_check_points=result.get("fact_check_points", []),
            )
            self.db.add(analysis)
            await self.db.flush()
            detection.analysis = analysis

        # Commit the transaction
        await self.db.commit()

        # Reload with eager loading to avoid lazy-load issues in async context
        result = await self.db.execute(
            select(Detection)
            .options(selectinload(Detection.analysis))
            .where(Detection.id == detection.id)
        )
        return result.scalar_one()

    async def detect_batch(
        self,
        user_id: uuid.UUID,
        contents: list[str],
        include_analysis: bool = True,
    ) -> list[Detection]:
        """
        Perform batch text detection using single API call.

        Args:
            user_id: The user performing the detection
            contents: List of text contents to analyze
            include_analysis: Whether to include detailed analysis

        Returns:
            List of detection records
        """
        if not contents:
            return []

        # 调用DeepSeek批量检测API（一次检测多条）
        results = await self.deepseek.detect_batch(contents)

        detections = []
        for i, (content, result) in enumerate(zip(contents, results)):
            try:
                # Determine risk level
                risk_level = RiskLevel.from_confidence(
                    result["confidence"],
                    result["is_rumor"],
                )

                # Create detection record
                detection = Detection(
                    user_id=user_id,
                    content=content,
                    is_rumor=result["is_rumor"],
                    confidence=result["confidence"],
                    risk_level=risk_level.value,
                    explanation=result["explanation"],
                    raw_response=result,
                )
                self.db.add(detection)
                await self.db.flush()

                # Create analysis record if requested
                if include_analysis:
                    analysis = Analysis(
                        detection_id=detection.id,
                        keywords=result.get("keywords", []),
                        sentiment=result.get("sentiment", "neutral"),
                        category=result.get("category", "other"),
                        sources=result.get("sources", []),
                        fact_check_points=result.get("fact_check_points", []),
                    )
                    self.db.add(analysis)
                    await self.db.flush()
                    detection.analysis = analysis

                detections.append(detection)
            except Exception as e:
                # Log error but continue with other items
                continue

        # Commit all at once
        await self.db.commit()

        # Reload with eager loading
        detection_ids = [d.id for d in detections]
        result = await self.db.execute(
            select(Detection)
            .options(selectinload(Detection.analysis))
            .where(Detection.id.in_(detection_ids))
        )
        return list(result.scalars().all())

    async def get_detection_by_id(
        self,
        detection_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Detection]:
        """Get detection by ID for a specific user."""
        result = await self.db.execute(
            select(Detection)
            .options(selectinload(Detection.analysis))
            .where(
                and_(
                    Detection.id == detection_id,
                    Detection.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_user_detections(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        is_rumor: Optional[bool] = None,
        risk_level: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[list[Detection], int]:
        """
        Get paginated detections for a user with optional filters.

        Returns:
            Tuple of (detections list, total count)
        """
        # Build base query
        query = select(Detection).where(Detection.user_id == user_id)

        # Apply filters
        if is_rumor is not None:
            query = query.where(Detection.is_rumor == is_rumor)
        if risk_level:
            query = query.where(Detection.risk_level == risk_level)
        if start_date:
            query = query.where(Detection.created_at >= start_date)
        if end_date:
            query = query.where(Detection.created_at <= end_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = (
            query.options(selectinload(Detection.analysis))
            .order_by(Detection.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        detections = list(result.scalars().all())

        return detections, total

    async def delete_detection(
        self,
        detection_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a detection record."""
        detection = await self.get_detection_by_id(detection_id, user_id)
        if not detection:
            return False

        await self.db.delete(detection)
        return True

    async def delete_batch(
        self,
        detection_ids: list[uuid.UUID],
        user_id: uuid.UUID,
    ) -> int:
        """Delete multiple detection records. Returns count of deleted items."""
        deleted = 0
        for detection_id in detection_ids:
            if await self.delete_detection(detection_id, user_id):
                deleted += 1
        return deleted

    def to_response(self, detection: Detection) -> DetectionResponse:
        """Convert detection model to response schema."""
        analysis = None
        if detection.analysis:
            analysis = AnalysisResult(
                keywords=detection.analysis.keywords or [],
                sentiment=detection.analysis.sentiment or "neutral",
                category=detection.analysis.category or "other",
                sources=detection.analysis.sources or [],
                fact_check_points=detection.analysis.fact_check_points or [],
                risk_indicators=detection.raw_response.get("risk_indicators", [])
                if detection.raw_response
                else [],
            )

        return DetectionResponse(
            id=detection.id,
            content=detection.content,
            is_rumor=detection.is_rumor,
            confidence=float(detection.confidence),
            risk_level=RiskLevel(detection.risk_level),
            explanation=detection.explanation or "",
            analysis=analysis,
            created_at=detection.created_at,
        )
