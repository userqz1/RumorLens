"""FastAPI application entry point."""

import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Weibo Rumor Detection Platform powered by DeepSeek",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Validation error handler - return friendly Chinese error messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with user-friendly messages."""
    errors = exc.errors()
    if errors:
        # Get the first error message
        first_error = errors[0]
        field = first_error.get("loc", ["", ""])[-1]
        msg = first_error.get("msg", "")

        # Map field names to Chinese
        field_names = {
            "email": "邮箱",
            "username": "用户名",
            "password": "密码",
        }
        field_cn = field_names.get(field, field)

        # Map common error messages to Chinese
        if "value is not a valid email address" in msg:
            detail = "请输入有效的邮箱地址"
        elif "String should have at least" in msg:
            if "6" in msg:
                detail = f"{field_cn}长度至少为6位"
            elif "3" in msg:
                detail = f"{field_cn}长度至少为3位"
            else:
                detail = f"{field_cn}长度不足"
        elif "Value error" in msg:
            # Extract the actual error message from Value error
            detail = msg.replace("Value error, ", "")
        else:
            detail = f"{field_cn}格式不正确: {msg}"

        return JSONResponse(
            status_code=422,
            content={"detail": detail},
        )

    return JSONResponse(
        status_code=422,
        content={"detail": "请求数据格式错误"},
    )


# Global exception handler for debugging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }
