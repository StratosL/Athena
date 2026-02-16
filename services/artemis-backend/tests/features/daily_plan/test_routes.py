"""Tests for daily plan routes."""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


class TestDailyPlanRoutes:
    """Tests for daily plan API endpoints."""

    def test_get_today_creates_plan(self, client: TestClient) -> None:
        """Test GET /daily-plans/today creates a plan if none exists."""
        response = client.get("/daily-plans/today")
        # Will return 200 with plan or 503 if DB not configured
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["date"] == str(datetime.now(UTC).date())
            assert data["total_tasks"] == 0
            assert data["completion_rate"] == 0.0

    def test_create_plan_for_date(self, client: TestClient) -> None:
        """Test POST /daily-plans creates new plan."""
        future_date = datetime.now(UTC).date() + timedelta(days=30)
        response = client.post(
            "/daily-plans",
            json={"date": str(future_date)},
        )
        assert response.status_code in [201, 503]

        if response.status_code == 201:
            data = response.json()
            assert data["date"] == str(future_date)

    def test_create_plan_duplicate_returns_409(self, client: TestClient) -> None:
        """Test POST same date returns 409 conflict."""
        test_date = datetime.now(UTC).date() + timedelta(days=31)

        # Create first plan
        response = client.post(
            "/daily-plans",
            json={"date": str(test_date)},
        )
        if response.status_code == 503:
            pytest.skip("Database not configured")

        assert response.status_code == 201

        # Try to create duplicate
        response = client.post(
            "/daily-plans",
            json={"date": str(test_date)},
        )
        assert response.status_code == 409

    def test_list_plans_returns_200(self, client: TestClient) -> None:
        """Test GET /daily-plans returns list."""
        response = client.get("/daily-plans")
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert isinstance(data["items"], list)

    def test_get_plan_by_id(self, client: TestClient) -> None:
        """Test GET /daily-plans/{id} returns plan."""
        # First create or get a plan
        response = client.get("/daily-plans/today")
        if response.status_code == 503:
            pytest.skip("Database not configured")

        plan_id = response.json()["id"]

        # Get by ID
        response = client.get(f"/daily-plans/{plan_id}")
        assert response.status_code == 200
        assert response.json()["id"] == plan_id

    def test_get_nonexistent_plan_returns_404(self, client: TestClient) -> None:
        """Test GET nonexistent plan returns 404."""
        response = client.get("/daily-plans/00000000-0000-0000-0000-000000000000")
        assert response.status_code in [404, 503]

    def test_assign_task_validates_slot(self, client: TestClient) -> None:
        """Test slot must be major, medium, or small."""
        # First get today's plan
        response = client.get("/daily-plans/today")
        if response.status_code == 503:
            pytest.skip("Database not configured")

        plan_id = response.json()["id"]

        # Try invalid slot
        response = client.post(
            f"/daily-plans/{plan_id}/tasks",
            json={"task_id": "00000000-0000-0000-0000-000000000001", "slot": "invalid"},
        )
        assert response.status_code == 422  # Validation error

    def test_remove_task_not_in_plan_returns_404(self, client: TestClient) -> None:
        """Test removing a task not in plan returns 404."""
        # First get today's plan
        response = client.get("/daily-plans/today")
        if response.status_code == 503:
            pytest.skip("Database not configured")

        plan_id = response.json()["id"]

        # Try to remove task that's not in plan
        response = client.delete(
            f"/daily-plans/{plan_id}/tasks/00000000-0000-0000-0000-999999999999"
        )
        assert response.status_code == 404


class TestSlotValidation:
    """Tests for slot type validation."""

    def test_slot_pattern_accepts_major(self, client: TestClient) -> None:
        """Test slot accepts 'major'."""
        response = client.get("/daily-plans/today")
        if response.status_code == 503:
            pytest.skip("Database not configured")

        plan_id = response.json()["id"]

        # major is valid slot (will fail at task validation, not slot validation)
        response = client.post(
            f"/daily-plans/{plan_id}/tasks",
            json={"task_id": "00000000-0000-0000-0000-000000000001", "slot": "major"},
        )
        # 400 means slot validation passed but task invalid (expected)
        # 422 would mean slot validation failed (not expected)
        assert response.status_code in [200, 400, 409]

    def test_slot_pattern_accepts_medium(self, client: TestClient) -> None:
        """Test slot accepts 'medium'."""
        response = client.get("/daily-plans/today")
        if response.status_code == 503:
            pytest.skip("Database not configured")

        plan_id = response.json()["id"]

        response = client.post(
            f"/daily-plans/{plan_id}/tasks",
            json={"task_id": "00000000-0000-0000-0000-000000000001", "slot": "medium"},
        )
        assert response.status_code in [200, 400, 409]

    def test_slot_pattern_accepts_small(self, client: TestClient) -> None:
        """Test slot accepts 'small'."""
        response = client.get("/daily-plans/today")
        if response.status_code == 503:
            pytest.skip("Database not configured")

        plan_id = response.json()["id"]

        response = client.post(
            f"/daily-plans/{plan_id}/tasks",
            json={"task_id": "00000000-0000-0000-0000-000000000001", "slot": "small"},
        )
        assert response.status_code in [200, 400, 409]

    def test_slot_pattern_rejects_invalid(self, client: TestClient) -> None:
        """Test slot rejects invalid values."""
        response = client.get("/daily-plans/today")
        if response.status_code == 503:
            pytest.skip("Database not configured")

        plan_id = response.json()["id"]

        for invalid_slot in ["large", "huge", "tiny", "MAJOR", "Medium"]:
            response = client.post(
                f"/daily-plans/{plan_id}/tasks",
                json={
                    "task_id": "00000000-0000-0000-0000-000000000001",
                    "slot": invalid_slot,
                },
            )
            assert response.status_code == 422, f"Slot '{invalid_slot}' should be rejected"
