"""Repository for analytics data aggregation."""

from datetime import UTC, date, datetime, timedelta
from typing import Any, cast

from supabase import Client

from app.core.logging import get_logger

logger = get_logger(__name__)


class AnalyticsRepository:
    """Repository for analytics data aggregation from existing tables."""

    def __init__(self, db: Client) -> None:
        """Initialize repository with Supabase client."""
        self.db = db

    def get_pomodoro_sessions_in_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        """Get completed pomodoro sessions within date range."""
        logger.info(
            "database.pomodoro_sessions_query_started",
            start_date=str(start_date),
            end_date=str(end_date),
        )

        start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=UTC)
        end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=UTC)

        result = (
            self.db.table("pomodoro_sessions")
            .select("id, started_at, duration_minutes, completed")
            .eq("completed", True)
            .gte("started_at", start_dt.isoformat())
            .lt("started_at", end_dt.isoformat())
            .order("started_at", desc=False)
            .execute()
        )

        sessions = cast(list[dict[str, Any]], result.data or [])
        logger.info(
            "database.pomodoro_sessions_query_completed",
            count=len(sessions),
        )
        return sessions

    def get_tasks_summary(self) -> dict[str, Any]:
        """Get task counts by quadrant and status."""
        logger.info("database.tasks_summary_query_started")

        result = (
            self.db.table("tasks")
            .select("id, quadrant, status, pomodoro_count, created_at, completed_at")
            .execute()
        )

        tasks = cast(list[dict[str, Any]], result.data or [])

        # Aggregate by quadrant
        quadrant_stats: dict[int, dict[str, int]] = {
            q: {"total": 0, "completed": 0} for q in [1, 2, 3, 4]
        }

        for task in tasks:
            q = task.get("quadrant", 1)
            quadrant_stats[q]["total"] += 1
            if task.get("status") == "completed":
                quadrant_stats[q]["completed"] += 1

        logger.info(
            "database.tasks_summary_query_completed",
            total_tasks=len(tasks),
        )

        return {
            "tasks": tasks,
            "quadrant_stats": quadrant_stats,
            "total": len(tasks),
            "completed": sum(1 for t in tasks if t.get("status") == "completed"),
        }

    def get_tasks_in_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        """Get tasks created or completed within date range."""
        start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=UTC)
        end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time(), tzinfo=UTC)

        # Tasks created in range
        created = (
            self.db.table("tasks")
            .select("id, quadrant, status, created_at, completed_at")
            .gte("created_at", start_dt.isoformat())
            .lt("created_at", end_dt.isoformat())
            .execute()
        )

        # Tasks completed in range (but created earlier)
        completed = (
            self.db.table("tasks")
            .select("id, quadrant, status, created_at, completed_at")
            .gte("completed_at", start_dt.isoformat())
            .lt("completed_at", end_dt.isoformat())
            .lt("created_at", start_dt.isoformat())
            .execute()
        )

        # Merge and deduplicate
        seen = set()
        merged: list[dict[str, Any]] = []
        for task in [*(created.data or []), *(completed.data or [])]:
            if task["id"] not in seen:
                seen.add(task["id"])
                merged.append(task)

        return merged

    def get_daily_plans_in_range(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        """Get daily plans within date range."""
        logger.info(
            "database.daily_plans_query_started",
            start_date=str(start_date),
            end_date=str(end_date),
        )

        result = (
            self.db.table("daily_plans")
            .select("id, date, major_task_id, medium_task_ids, small_task_ids")
            .gte("date", str(start_date))
            .lte("date", str(end_date))
            .execute()
        )

        plans = cast(list[dict[str, Any]], result.data or [])
        logger.info(
            "database.daily_plans_query_completed",
            count=len(plans),
        )
        return plans

    def get_task_by_ids(self, task_ids: list[str]) -> list[dict[str, Any]]:
        """Get tasks by list of IDs."""
        if not task_ids:
            return []

        result = self.db.table("tasks").select("id, status").in_("id", task_ids).execute()

        return cast(list[dict[str, Any]], result.data or [])
