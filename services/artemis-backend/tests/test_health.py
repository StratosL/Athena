"""Tests for health check endpoint."""

from fastapi.testclient import TestClient


def test_health_endpoint_returns_200(client: TestClient) -> None:
    """Test that health endpoint returns 200 status."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_healthy_status(client: TestClient) -> None:
    """Test that health endpoint returns healthy status."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint_returns_app_info(client: TestClient) -> None:
    """Test that root endpoint returns application info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
