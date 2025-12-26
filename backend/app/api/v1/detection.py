"""Detection API routes."""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.detection import (
    BatchDetectionRequest,
    BatchDetectionResponse,
    DetectionRequest,
    DetectionResponse,
    PropagationResponse,
)
from app.services.detection_service import DetectionService

router = APIRouter()


@router.post("/single", response_model=DetectionResponse)
async def detect_single(
    request: DetectionRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> DetectionResponse:
    """Perform single text rumor detection."""
    detection_service = DetectionService(db)
    detection = await detection_service.detect_single(
        user_id=current_user.id,
        request=request,
    )
    return detection_service.to_response(detection)


@router.post("/batch", response_model=BatchDetectionResponse)
async def detect_batch(
    request: BatchDetectionRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> BatchDetectionResponse:
    """Perform batch text rumor detection."""
    detection_service = DetectionService(db)

    detections = await detection_service.detect_batch(
        user_id=current_user.id,
        contents=request.contents,
        include_analysis=request.include_analysis,
    )

    results = [detection_service.to_response(d) for d in detections]

    return BatchDetectionResponse(
        total=len(request.contents),
        success=len(results),
        failed=len(request.contents) - len(results),
        results=results,
    )


@router.get("/{detection_id}", response_model=DetectionResponse)
async def get_detection(
    detection_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> DetectionResponse:
    """Get detection by ID."""
    detection_service = DetectionService(db)
    detection = await detection_service.get_detection_by_id(
        detection_id=detection_id,
        user_id=current_user.id,
    )

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    return detection_service.to_response(detection)


@router.get("/{detection_id}/analysis")
async def get_detection_analysis(
    detection_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """Get detailed analysis for a detection."""
    detection_service = DetectionService(db)
    detection = await detection_service.get_detection_by_id(
        detection_id=detection_id,
        user_id=current_user.id,
    )

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    response = detection_service.to_response(detection)
    if not response.analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not available for this detection",
        )

    return response.analysis


@router.get("/{detection_id}/propagation", response_model=PropagationResponse)
async def get_propagation(
    detection_id: uuid.UUID,
    current_user: CurrentUser,
    db: DbSession,
) -> PropagationResponse:
    """Get propagation path for a detection."""
    detection_service = DetectionService(db)
    detection = await detection_service.get_detection_by_id(
        detection_id=detection_id,
        user_id=current_user.id,
    )

    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found",
        )

    # Return propagation nodes (may be empty if not available)
    from app.schemas.detection import PropagationNode

    nodes = [
        PropagationNode(
            node_id=node.node_id,
            parent_id=node.parent_id,
            content=node.content,
            user_info=node.user_info,
            engagement=node.engagement,
            timestamp=node.timestamp,
        )
        for node in detection.propagation_nodes
    ]

    return PropagationResponse(
        detection_id=detection.id,
        nodes=nodes,
    )
