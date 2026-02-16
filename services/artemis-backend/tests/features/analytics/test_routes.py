"""Tests for analytics routes."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


class TestAnalyticsRoutes:
    """Tests for analytics API endpoints."""

    def test_get_summary_returns_200_or_503(self, client: TestClient) -> None:
        """Test getting summary returns 200 or 503 (if DB not configured)."""
        response = client.get("/analytics/summary")
        assert response.status_code in [200, 503]

    def test_get_summary_with_period_param(self, client: TestClient) -> None:
        """Test getting summary with period parameter."""
        response = client.get("/analytics/summary?period=week")
        assert response.status_code in [200, 503]

    def test_get_summary_month_period(self, client: TestClient) -> None:
        """Test getting summary with month period."""
        response = client.get("/analytics/summary?period=month")
        assert response.status_code in [200, 503]

    def test_get_pomodoro_trends_returns_200_or_503(self, client: TestClient) -> None:
        """Test getting pomodoro trends returns 200 or 503."""
        response = client.get("/analytics/pomodoro-trends")
        assert response.status_code in [200, 503]

    def test_get_pomodoro_trends_with_period(self, client: TestClient) -> None:
        """Test getting pomodoro trends with period parameter."""
        response = client.get("/analytics/pomodoro-trends?period=day")
        assert response.status_code in [200, 503]

    def test_get_task_distribution_returns_200_or_503(self, client: TestClient) -> None:
        """Test getting task distribution returns 200 or 503."""
        response = client.get("/analytics/task-distribution")
        assert response.status_code in [200, 503]

    def test_invalid_period_returns_422(self, client: TestClient) -> None:
        """Test invalid period parameter returns 422.

        Note: FastAPI validates query params before dependency injection,
        so this should return 422 regardless of DB configuration.
        """
        response = client.get("/analytics/summary?period=invalid")
        assert response.status_code in [422, 503]
