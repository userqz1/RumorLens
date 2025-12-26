"""Tests for detection endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_deepseek_response():
    """Mock DeepSeek API response."""
    return {
        "is_rumor": True,
        "confidence": 0.35,
        "explanation": "This content contains unverified claims.",
        "keywords": ["test", "rumor"],
        "sentiment": "negative",
        "category": "social",
        "fact_check_points": ["Source not verified"],
        "risk_indicators": ["Unverified claims"],
    }


@pytest.mark.asyncio
async def test_detect_single_unauthorized(client: AsyncClient):
    """Test detection without authentication."""
    response = await client.post(
        "/api/v1/detection/single",
        json={"content": "Test content"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_detect_single(client: AsyncClient, mock_deepseek_response):
    """Test single text detection."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123",
        },
    )
    token = login_response.json()["access_token"]

    # Mock DeepSeek API
    with patch(
        "app.services.deepseek_service.DeepSeekService.detect_rumor",
        new_callable=AsyncMock,
        return_value=mock_deepseek_response,
    ):
        response = await client.post(
            "/api/v1/detection/single",
            json={"content": "This is a test rumor content"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["is_rumor"] is True
    assert data["confidence"] == 0.35
    assert data["risk_level"] == "critical"
    assert "analysis" in data


@pytest.mark.asyncio
async def test_detect_batch(client: AsyncClient, mock_deepseek_response):
    """Test batch detection."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123",
        },
    )
    token = login_response.json()["access_token"]

    # Mock DeepSeek API
    with patch(
        "app.services.deepseek_service.DeepSeekService.detect_rumor",
        new_callable=AsyncMock,
        return_value=mock_deepseek_response,
    ):
        response = await client.post(
            "/api/v1/detection/batch",
            json={
                "contents": ["Content 1", "Content 2", "Content 3"],
                "include_analysis": True,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["success"] == 3
    assert len(data["results"]) == 3


@pytest.mark.asyncio
async def test_get_history(client: AsyncClient, mock_deepseek_response):
    """Test getting detection history."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123",
        },
    )
    token = login_response.json()["access_token"]

    # Create a detection
    with patch(
        "app.services.deepseek_service.DeepSeekService.detect_rumor",
        new_callable=AsyncMock,
        return_value=mock_deepseek_response,
    ):
        await client.post(
            "/api/v1/detection/single",
            json={"content": "Test content"},
            headers={"Authorization": f"Bearer {token}"},
        )

    # Get history
    response = await client.get(
        "/api/v1/history",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
