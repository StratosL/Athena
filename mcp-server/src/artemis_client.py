"""Async HTTP client wrapper for the Artemis REST API.

Adapts the Artemis endpoints into a clean internal interface
that MCP tools consume. Uses httpx for async HTTP.
"""

import logging

import httpx

logger = logging.getLogger(__name__)


class ArtemisClient:
    """Async HTTP client for the Artemis REST API."""

    def __init__(self, base_url: str) -> None:
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self.client.aclose()

    async def create_task(
        self,
        title: str,
        quadrant: int,
        description: str | None = None,
        due_date: str | None = None,
    ) -> dict:
        """Create a new task in Artemis."""
        body: dict = {"title": title, "quadrant": quadrant}
        if description:
            body["description"] = description
        if due_date:
            body["due_date"] = due_date
        resp = await self.client.post("/tasks", json=body)
        resp.raise_for_status()
        return resp.json()

    async def list_tasks(
        self,
        quadrant: int | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """List tasks with optional filters."""
        params: dict = {"limit": limit, "offset": offset}
        if quadrant is not None:
            params["quadrant"] = quadrant
        if status:
            params["status"] = status
        resp = await self.client.get("/tasks", params=params)
        resp.raise_for_status()
        return resp.json()

    async def complete_task(self, task_id: str) -> dict:
        """Mark a task as completed."""
        resp = await self.client.post(f"/tasks/{task_id}/complete")
        resp.raise_for_status()
        return resp.json()

    async def get_daily_plan(self) -> dict:
        """Get today's daily plan (auto-creates if missing)."""
        resp = await self.client.get("/daily-plans/today")
        resp.raise_for_status()
        return resp.json()

    async def assign_to_plan(self, plan_id: str, task_id: str, slot: str) -> dict:
        """Assign a task to a daily plan slot."""
        body = {"task_id": task_id, "slot": slot}
        resp = await self.client.post(f"/daily-plans/{plan_id}/tasks", json=body)
        resp.raise_for_status()
        return resp.json()

    async def get_analytics(self, period: str = "week") -> dict:
        """Get productivity analytics summary."""
        resp = await self.client.get("/analytics/summary", params={"period": period})
        resp.raise_for_status()
        return resp.json()

    async def start_pomodoro(self, task_id: str | None = None, duration_minutes: int = 25) -> dict:
        """Start a pomodoro session."""
        body: dict = {}
        if task_id:
            body["task_id"] = task_id
        if duration_minutes != 25:
            body["duration_minutes"] = duration_minutes
        resp = await self.client.post("/pomodoro/start", json=body)
        resp.raise_for_status()
        return resp.json()

    async def health_check(self) -> dict:
        """Check Artemis backend health."""
        resp = await self.client.get("/health")
        resp.raise_for_status()
        return resp.json()
