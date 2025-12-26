"""History management API routes."""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbSession
from app.schemas.analysis import HistoryStats, RiskDistribution
from app.schemas.common import Message, PaginatedResponse
from app.schemas.detection import DetectionResponse
from app.services.detection_service import DetectionService

router = APIRouter()


class BatchDeleteRequest(BaseModel):
    """Request schema for batch delete."""

    ids: list[uuid.UUID]


@router.get("", response_model=PaginatedResponse[DetectionResponse])
async def get_history(
    current_user: CurrentUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_rumor: Optional[bool] = None,
    risk_level: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> PaginatedResponse[DetectionResponse]:
    """Get paginated detection history with optional filters."""
    detection_service = DetectionService(db)

    detections, total = await detection_service.get_user_detections(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        is_rumor=is_rumor,
        risk_level=risk_level,
        start_date=start_date,
        end_date=end_date,
    )

    items = [detection_service.to_response(d) for d in detections]

    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=HistoryStats)
async def get_history_stats(
    current_user: CurrentUser,
    db: DbSession,
) -> HistoryStats:
    """Get statistics for user's detection history."""
    detection_service = DetectionService(db)

    # Get all detections for stats
    detections, total = await detection_service.get_user_detections(
        user_id=current_user.id,
        page=1,
        page_size=10000,  # Get all for stats
    )

    # Calculate statistics
    rumors_count = sum(1 for d in detections if d.is_rumor)
    verified_count = total - rumors_count

    risk_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for d in detections:
        if d.risk_level in risk_counts:
            risk_counts[d.risk_level] += 1

    return HistoryStats(
        total_records=total,
        rumors_count=rumors_count,
        verified_count=verified_count,
        by_risk_level=RiskDistribution(**risk_counts),
    )


@router.delete("/{detection_id}", response_model=Message)
async def delete_history_item(
    detection_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> Message:
    """Delete a single detection record."""
    detection_service = DetectionService(db)

    deleted = await detection_service.delete_detection(
        detection_id=detection_id,
        user_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    return Message(message="Detection deleted successfully")


@router.delete("/batch", response_model=Message)
async def delete_history_batch(
    request: BatchDeleteRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> Message:
    """Delete multiple detection records."""
    detection_service = DetectionService(db)

    deleted_count = await detection_service.delete_batch(
        detection_ids=request.ids,
        user_id=current_user.id,
    )

    return Message(message=f"Deleted {deleted_count} records")
