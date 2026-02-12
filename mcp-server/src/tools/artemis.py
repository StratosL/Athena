"""Artemis MCP tools — proxy to the Artemis REST API.

Seven tools covering task management, daily planning, analytics, and pomodoro:
- artemis_create_task
- artemis_list_tasks
- artemis_complete_task
- artemis_get_daily_plan
- artemis_assign_to_plan
- artemis_get_analytics
- artemis_start_pomodoro
"""

import json
import logging

import httpx

from src.server import artemis_client, mcp

logger = logging.getLogger(__name__)


@mcp.tool()
async def artemis_create_task(
    title: str,
    quadrant: int,
    description: str = "",
    due_date: str = "",
) -> str:
    """Create a new task in Artemis with Eisenhower Matrix classification.

    Args:
        title: Task title (1-200 chars).
        quadrant: Eisenhower quadrant (1=urgent+important, 2=not-urgent+important, 3=urgent+not-important, 4=not-urgent+not-important).
        description: Optional task description.
        due_date: Optional due date in ISO format (e.g. 2026-02-20).
    """
    try:
        result = await artemis_client.create_task(
            title=title,
            quadrant=quadrant,
            description=description or None,
            due_date=due_date or None,
        )
        return json.dumps(result)
    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"Artemis returned {e.response.status_code}: {e.response.text}"}
        )
    except httpx.ConnectError:
        return json.dumps({"error": "Cannot connect to Artemis. Is it running?"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


@mcp.tool()
async def artemis_list_tasks(
    quadrant: int = 0,
    status: str = "",
) -> str:
    """List tasks from Artemis with optional filters.

    Args:
        quadrant: Filter by Eisenhower quadrant (1-4). 0 = no filter.
        status: Filter by status (e.g. "pending", "completed"). Empty = no filter.
    """
    try:
        result = await artemis_client.list_tasks(
            quadrant=quadrant if quadrant > 0 else None,
            status=status or None,
        )
        return json.dumps(result)
    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"Artemis returned {e.response.status_code}: {e.response.text}"}
        )
    except httpx.ConnectError:
        return json.dumps({"error": "Cannot connect to Artemis. Is it running?"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


@mcp.tool()
async def artemis_complete_task(task_id: str) -> str:
    """Mark an Artemis task as completed.

    Args:
        task_id: The ID of the task to complete.
    """
    try:
        result = await artemis_client.complete_task(task_id)
        return json.dumps(result)
    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"Artemis returned {e.response.status_code}: {e.response.text}"}
        )
    except httpx.ConnectError:
        return json.dumps({"error": "Cannot connect to Artemis. Is it running?"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


@mcp.tool()
async def artemis_get_daily_plan() -> str:
    """Get today's daily plan from Artemis with expanded task details."""
    try:
        result = await artemis_client.get_daily_plan()
        return json.dumps(result)
    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"Artemis returned {e.response.status_code}: {e.response.text}"}
        )
    except httpx.ConnectError:
        return json.dumps({"error": "Cannot connect to Artemis. Is it running?"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


@mcp.tool()
async def artemis_assign_to_plan(plan_id: str, task_id: str, slot: str) -> str:
    """Assign a task to a slot in today's daily plan.

    Args:
        plan_id: The daily plan ID.
        task_id: The task ID to assign.
        slot: Plan slot — must be "major", "medium", or "small".
    """
    if slot not in ("major", "medium", "small"):
        return json.dumps(
            {"error": f"Invalid slot '{slot}'. Must be 'major', 'medium', or 'small'."}
        )
    try:
        result = await artemis_client.assign_to_plan(plan_id, task_id, slot)
        return json.dumps(result)
    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"Artemis returned {e.response.status_code}: {e.response.text}"}
        )
    except httpx.ConnectError:
        return json.dumps({"error": "Cannot connect to Artemis. Is it running?"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


@mcp.tool()
async def artemis_get_analytics(period: str = "week") -> str:
    """Get productivity analytics from Artemis.

    Args:
        period: Time period — "day", "week", or "month".
    """
    try:
        result = await artemis_client.get_analytics(period)
        return json.dumps(result)
    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"Artemis returned {e.response.status_code}: {e.response.text}"}
        )
    except httpx.ConnectError:
        return json.dumps({"error": "Cannot connect to Artemis. Is it running?"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})


@mcp.tool()
async def artemis_start_pomodoro(task_id: str = "") -> str:
    """Start a pomodoro timer session in Artemis.

    Args:
        task_id: Optional task ID to link the session to. Empty = unlinked session.
    """
    try:
        result = await artemis_client.start_pomodoro(
            task_id=task_id or None,
        )
        return json.dumps(result)
    except httpx.HTTPStatusError as e:
        return json.dumps(
            {"error": f"Artemis returned {e.response.status_code}: {e.response.text}"}
        )
    except httpx.ConnectError:
        return json.dumps({"error": "Cannot connect to Artemis. Is it running?"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {e}"})
