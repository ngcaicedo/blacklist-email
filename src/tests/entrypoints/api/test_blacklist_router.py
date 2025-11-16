from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status

from domain.schemas import (
    BlacklistCheckResponse,
    BlacklistCreateResponse,
)
from domain.use_cases import AddEmailToBlacklistUseCase, CheckEmailInBlacklistUseCase
from assembly import get_add_email_use_case, get_check_email_use_case
from entrypoints.api.dependencies import verify_token
from entrypoints.api.main import app
from errors import DuplicateEmailError


class TestBlacklistRouter:
    """Unit tests for blacklist router endpoints."""

    @pytest.mark.asyncio
    async def test_post_blacklists_success(self):
        """Test POST /blacklists endpoint successfully adds email to blacklist."""
        email = "spam@example.com"
        app_uuid = "123e4567-e89b-12d3-a456-426614174000"
        blocked_reason = "User reported for spam"
        
        blocked_at = datetime.now(timezone.utc)
        mock_response = BlacklistCreateResponse(
            message="Email added to blacklist successfully test",
            email=email,
            blocked_at=blocked_at,
        )
        
        # Mock use case
        mock_use_case = Mock(spec=AddEmailToBlacklistUseCase)
        mock_use_case.execute = AsyncMock(return_value=mock_response)
        
        # Override dependencies
        async def mock_verify_token():
            return "test-token"
        
        app.dependency_overrides[verify_token] = mock_verify_token
        app.dependency_overrides[get_add_email_use_case] = lambda: mock_use_case
        
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/blacklists",
                    json={
                        "email": email,
                        "app_uuid": app_uuid,
                        "blocked_reason": blocked_reason,
                    },
                    headers={"Authorization": "Bearer test-token"},
                )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["message"] == "Email added to blacklist successfully test"
            assert data["email"] == email
            assert "blocked_at" in data
            mock_use_case.execute.assert_called_once()
            
            # Verify the call arguments
            call_args = mock_use_case.execute.call_args
            assert call_args[0][0].email == email
            assert call_args[0][0].app_uuid == UUID(app_uuid)
            assert call_args[0][0].blocked_reason == blocked_reason
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_post_blacklists_without_reason(self):
        """Test POST /blacklists endpoint works without blocked_reason."""
        email = "spam@example.com"
        app_uuid = "123e4567-e89b-12d3-a456-426614174000"
        
        blocked_at = datetime.now(timezone.utc)
        mock_response = BlacklistCreateResponse(
            message="Email added to blacklist successfully",
            email=email,
            blocked_at=blocked_at,
        )
        
        # Mock use case
        mock_use_case = Mock(spec=AddEmailToBlacklistUseCase)
        mock_use_case.execute = AsyncMock(return_value=mock_response)
        
        # Override dependencies
        async def mock_verify_token():
            return "test-token"
        
        app.dependency_overrides[verify_token] = mock_verify_token
        app.dependency_overrides[get_add_email_use_case] = lambda: mock_use_case
        
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/blacklists",
                    json={
                        "email": email,
                        "app_uuid": app_uuid,
                    },
                    headers={"Authorization": "Bearer test-token"},
                )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["email"] == email
            mock_use_case.execute.assert_called_once()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_post_blacklists_duplicate_email_error(self):
        """Test POST /blacklists endpoint returns 409 on duplicate email."""
        email = "spam@example.com"
        app_uuid = "123e4567-e89b-12d3-a456-426614174000"
        
        # Mock use case to raise DuplicateEmailError
        mock_use_case = Mock(spec=AddEmailToBlacklistUseCase)
        mock_use_case.execute = AsyncMock(
            side_effect=DuplicateEmailError(f"Email {email} already exists in blacklist")
        )
        
        # Override dependencies
        async def mock_verify_token():
            return "test-token"
        
        app.dependency_overrides[verify_token] = mock_verify_token
        app.dependency_overrides[get_add_email_use_case] = lambda: mock_use_case
        
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/blacklists",
                    json={
                        "email": email,
                        "app_uuid": app_uuid,
                        "blocked_reason": "Duplicate test",
                    },
                    headers={"Authorization": "Bearer test-token"},
                )
            
            assert response.status_code == status.HTTP_409_CONFLICT
            data = response.json()
            assert "detail" in data
            assert f"Email {email} already exists in blacklist" in data["detail"]
            mock_use_case.execute.assert_called_once()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_post_blacklists_unauthorized(self):
        """Test POST /blacklists endpoint returns 401 without token."""
        email = "spam@example.com"
        app_uuid = "123e4567-e89b-12d3-a456-426614174000"
        
        # Mock verify_token to raise HTTPException
        async def mock_verify_token():
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post(
                    "/blacklists",
                    json={
                        "email": email,
                        "app_uuid": app_uuid,
                    },
                )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert "detail" in data
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_blacklists_email_blocked(self):
        """Test GET /blacklists/{email} endpoint returns blocked status for blocked email."""
        email = "spam@example.com"
        blocked_at = datetime.now(timezone.utc)
        
        mock_response = BlacklistCheckResponse(
            email=email,
            is_blocked=True,
            blocked_reason="User reported for spam",
            blocked_at=blocked_at,
        )
        
        # Mock use case
        mock_use_case = Mock(spec=CheckEmailInBlacklistUseCase)
        mock_use_case.execute = AsyncMock(return_value=mock_response)
        
        # Override dependencies
        app.dependency_overrides[verify_token] = lambda: "test-token"
        app.dependency_overrides[get_check_email_use_case] = lambda: mock_use_case
        
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/blacklists/{email}",
                    headers={"Authorization": "Bearer test-token"},
                )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["email"] == email
            assert data["is_blocked"] is True
            assert data["blocked_reason"] == "User reported for spam"
            assert "blocked_at" in data
            mock_use_case.execute.assert_called_once_with(email)
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_blacklists_email_not_blocked(self):
        """Test GET /blacklists/{email} endpoint returns not blocked status for clean email."""
        email = "clean@example.com"
        
        mock_response = BlacklistCheckResponse(
            email=email,
            is_blocked=False,
            blocked_reason=None,
            blocked_at=None,
        )
        
        # Mock use case
        mock_use_case = Mock(spec=CheckEmailInBlacklistUseCase)
        mock_use_case.execute = AsyncMock(return_value=mock_response)
        
        # Override dependencies
        app.dependency_overrides[verify_token] = lambda: "test-token"
        app.dependency_overrides[get_check_email_use_case] = lambda: mock_use_case
        
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/blacklists/{email}",
                    headers={"Authorization": "Bearer test-token"},
                )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["email"] == email
            assert data["is_blocked"] is False
            assert data["blocked_reason"] is None
            assert data["blocked_at"] is None
            mock_use_case.execute.assert_called_once_with(email)
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_blacklists_email_unauthorized(self):
        """Test GET /blacklists/{email} endpoint returns 401 without token."""
        email = "clean@example.com"
        
        # Mock verify_token to raise HTTPException
        async def mock_verify_token():
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.get(
                    f"/blacklists/{email}",
                )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert "detail" in data
        finally:
            app.dependency_overrides.clear()
