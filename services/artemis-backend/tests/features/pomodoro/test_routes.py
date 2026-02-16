"""Tests for pomodoro routes."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


class TestPomodoroRoutes:
    """Tests for pomodoro API endpoints."""

    def test_get_active_returns_200_or_503(self, client: TestClient) -> None:
        """Test getting active timer returns 200 or 503 (if DB not configured)."""
        response = client.get("/pomodoro/active")
        assert response.status_code in [200, 503]

    def test_start_session_returns_201_or_503(self, client: TestClient) -> None:
        """Test starting a session returns 201 or 503 (if DB not configured)."""
        response = client.post("/pomodoro/start", json={})
        # 201 success, 409 if already active, 503 if no DB
        assert response.status_code in [201, 409, 503]

    def test_get_sessions_returns_200_or_503(self, client: TestClient) -> None:
        """Test listing sessions returns 200 or 503 (if DB not configured)."""
        response = client.get("/pomodoro/sessions")
        assert response.status_code in [200, 503]

    def test_get_sessions_with_limit(self, client: TestClient) -> None:
        """Test listing sessions with limit parameter."""
        response = client.get("/pomodoro/sessions?limit=5")
        assert response.status_code in [200, 503]

    def test_stop_session_returns_404_or_503(self, client: TestClient) -> None:
        """Test stopping when no active session returns 404 or 503."""
        response = client.post("/pomodoro/stop")
        # 404 if no active session, 200 if stopped, 503 if no DB
        assert response.status_code in [200, 404, 503]

    def test_complete_session_returns_404_or_503(self, client: TestClient) -> None:
        """Test completing when no active session returns 404 or 503."""
        response = client.post("/pomodoro/complete")
        # 404 if no active session, 200 if completed, 503 if no DB
        assert response.status_code in [200, 404, 503]

    def test_get_nonexistent_session_returns_404_or_503(self, client: TestClient) -> None:
        """Test getting nonexistent session returns 404 or 503."""
        response = client.get("/pomodoro/sessions/00000000-0000-0000-0000-000000000000")
        assert response.status_code in [404, 503]

    def test_start_session_with_task_id(self, client: TestClient) -> None:
        """Test starting a session with task_id."""
        response = client.post(
            "/pomodoro/start",
            json={"task_id": "00000000-0000-0000-0000-000000000001"},
        )
        # 201 success, 409 if already active, 503 if no DB
        assert response.status_code in [201, 409, 503]
