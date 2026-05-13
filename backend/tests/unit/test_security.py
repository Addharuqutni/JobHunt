"""
Tests for security, configuration validation, and API authentication.
Covers production secret enforcement, API key verification, and query parameter limits.
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestConfigValidation:
    """Tests for production configuration enforcement."""

    def test_production_rejects_default_api_key(self):
        """Production environment must reject the default dev API key."""
        from pydantic import ValidationError
        from app.core.config import Settings

        with pytest.raises(ValidationError, match="API_KEY must be set"):
            Settings(APP_ENV="production", API_KEY="dev-secret-key-123")

    def test_production_rejects_default_db_password(self):
        """Production environment must reject the default database password."""
        from pydantic import ValidationError
        from app.core.config import Settings

        with pytest.raises(ValidationError, match="POSTGRES_PASSWORD must be changed"):
            Settings(
                APP_ENV="production",
                API_KEY="strong-production-key-xyz",
                POSTGRES_PASSWORD="jobsentinel123",
            )

    def test_production_accepts_strong_secrets(self):
        """Production environment accepts properly configured secrets."""
        from app.core.config import Settings

        s = Settings(
            APP_ENV="production",
            API_KEY="my-strong-production-key-2026",
            POSTGRES_PASSWORD="super-secure-db-pass",
        )
        assert s.APP_ENV == "production"
        assert s.API_KEY == "my-strong-production-key-2026"

    def test_development_allows_default_secrets(self):
        """Development environment allows default secrets for convenience."""
        from app.core.config import Settings

        s = Settings(APP_ENV="development")
        assert s.API_KEY == "dev-secret-key-123"
        assert s.is_development is True

    def test_cors_origins_list_includes_frontend_url(self):
        """CORS origins list always includes the FRONTEND_URL."""
        from app.core.config import Settings

        s = Settings(
            FRONTEND_URL="http://myapp.com",
            CORS_ORIGINS="http://localhost:3000",
        )
        assert "http://myapp.com" in s.cors_origins_list
        assert "http://localhost:3000" in s.cors_origins_list

    def test_cors_origins_deduplicates_frontend_url(self):
        """FRONTEND_URL is not duplicated if already in CORS_ORIGINS."""
        from app.core.config import Settings

        s = Settings(
            FRONTEND_URL="http://localhost:5173",
            CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173",
        )
        assert s.cors_origins_list.count("http://localhost:5173") == 1


class TestAPIAuthentication:
    """Tests for API key enforcement on protected endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client that lets the exception handler return 500."""
        from app.api.app import create_app
        app = create_app()
        return TestClient(app, raise_server_exceptions=False)

    def test_health_endpoint_no_api_key(self, client):
        """Health endpoint must be accessible without API key."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_protected_endpoint_rejects_missing_key(self, client):
        """Protected endpoints must reject requests without API key."""
        response = client.get("/api/jobs")
        assert response.status_code == 401

    def test_protected_endpoint_rejects_invalid_key(self, client):
        """Protected endpoints must reject requests with wrong API key."""
        response = client.get("/api/jobs", headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 401

    def test_protected_endpoint_accepts_valid_key(self, client):
        """Protected endpoints must accept requests with valid API key (auth passes)."""
        from app.core.config import settings
        response = client.get(
            "/api/jobs",
            headers={"X-API-Key": settings.API_KEY},
        )
        # Auth must pass (not 401). 200 = DB available, 500 = DB unavailable.
        assert response.status_code in (200, 500)


class TestQueryParameterValidation:
    """Tests for input validation on API query parameters."""

    @pytest.fixture
    def client(self):
        """Create a test client that lets the exception handler return 500."""
        from app.api.app import create_app
        app = create_app()
        return TestClient(app, raise_server_exceptions=False)

    @pytest.fixture
    def auth_headers(self):
        """Return valid auth headers for protected endpoints."""
        from app.core.config import settings
        return {"X-API-Key": settings.API_KEY}

    def test_jobs_limit_too_large_rejected(self, client, auth_headers):
        """Limit exceeding 500 must be rejected with 422."""
        response = client.get("/api/jobs?limit=1000", headers=auth_headers)
        assert response.status_code == 422

    def test_jobs_limit_zero_rejected(self, client, auth_headers):
        """Limit of 0 must be rejected with 422."""
        response = client.get("/api/jobs?limit=0", headers=auth_headers)
        assert response.status_code == 422

    def test_jobs_limit_negative_rejected(self, client, auth_headers):
        """Negative limit must be rejected with 422."""
        response = client.get("/api/jobs?limit=-5", headers=auth_headers)
        assert response.status_code == 422

    def test_jobs_search_too_long_rejected(self, client, auth_headers):
        """Search query exceeding 200 chars must be rejected with 422."""
        long_search = "a" * 201
        response = client.get(f"/api/jobs?search={long_search}", headers=auth_headers)
        assert response.status_code == 422

    def test_settings_update_rejects_unknown_keys(self, client, auth_headers):
        """Settings update must reject unknown keys."""
        response = client.post(
            "/api/settings",
            json={"settings": {"unknown_key": "value"}},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_settings_update_rejects_empty_payload(self, client, auth_headers):
        """Settings update must reject empty settings dict."""
        response = client.post(
            "/api/settings",
            json={"settings": {}},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_settings_update_accepts_valid_keys(self, client, auth_headers):
        """Settings update must accept allowlisted keys (validation passes)."""
        response = client.post(
            "/api/settings",
            json={"settings": {"keywords": ["python", "react"]}},
            headers=auth_headers,
        )
        # Validation must pass (not 422). 200 = DB available, 500 = DB unavailable.
        assert response.status_code in (200, 500)
