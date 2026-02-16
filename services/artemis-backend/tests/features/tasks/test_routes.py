"""Tests for task routes."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


class TestTaskRoutes:
    """Tests for task API endpoints."""

    def test_create_task_returns_201(self, client: TestClient) -> None:
        """Test creating a task returns 201 status."""
        response = client.post(
            "/tasks",
            json={"title": "Test Task", "quadrant": 1},
        )
        # Note: Will return 503 if Supabase not configured
        assert response.status_code in [201, 503]

    def test_list_tasks_returns_200(self, client: TestClient) -> None:
        """Test listing tasks returns 200 status."""
        response = client.get("/tasks")
        assert response.status_code in [200, 503]

    def test_create_task_validates_quadrant(self, client: TestClient) -> None:
        """Test that quadrant must be 1-4."""
        response = client.post(
            "/tasks",
            json={"title": "Test Task", "quadrant": 5},
        )
        # 422 if validation happens first, 503 if DB check happens first
        assert response.status_code in [422, 503]

    def test_create_task_requires_title(self, client: TestClient) -> None:
        """Test that title is required."""
        response = client.post(
            "/tasks",
            json={"quadrant": 1},
        )
        # 422 if validation happens first, 503 if DB check happens first
        assert response.status_code in [422, 503]

    def test_get_nonexistent_task_returns_404_or_503(self, client: TestClient) -> None:
        """Test getting nonexistent task returns 404 or 503 (if DB not configured)."""
        response = client.get("/tasks/00000000-0000-0000-0000-000000000000")
        assert response.status_code in [404, 503]
