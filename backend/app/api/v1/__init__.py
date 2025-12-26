"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1 import auth, detection, history, analysis, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(detection.router, prefix="/detection", tags=["Detection"])
api_router.include_router(history.router, prefix="/history", tags=["History"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
