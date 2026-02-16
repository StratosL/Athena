"""Daily plan repository for Supabase data access."""

from datetime import date
from typing import Any, cast

from postgrest import CountMethod
from supabase import Client

from app.core.logging import get_logger
from app.features.daily_plan.exceptions import (
    DailyPlanExistsError,
    DailyPlanNotFoundError,
)

logger = get_logger(__name__)


class DailyPlanRepository:
    """Repository for daily plan CRUD operations with Supabase."""

    def __init__(self, db: Client) -> None:
        """Initialize repository with Supabase client."""
        self.db = db
        self.table = "daily_plans"
        self.tasks_table = "tasks"

    def create(self, plan_date: date) -> dict[str, Any]:
        """Create a new daily plan."""
        # Check if plan already exists for this date
        existing = self.get_by_date(plan_date, raise_not_found=False)
        if existing:
            raise DailyPlanExistsError(str(plan_date))

        payload = {
            "date": str(plan_date),
            "medium_task_ids": [],
            "small_task_ids": [],
        }

        result = self.db.table(self.table).insert(payload).execute()

        if not result.data:
            raise RuntimeError("Failed to create daily plan")

        return cast(dict[str, Any], result.data[0])

    def get_by_id(self, plan_id: str) -> dict[str, Any]:
        """Get a daily plan by ID."""
        result = self.db.table(self.table).select("*").eq("id", plan_id).execute()

        if not result.data:
            raise DailyPlanNotFoundError(plan_id)

        return cast(dict[str, Any], result.data[0])

    def get_by_date(self, plan_date: date, raise_not_found: bool = True) -> dict[str, Any] | None:
        """Get a daily plan by date."""
        result = self.db.table(self.table).select("*").eq("date", str(plan_date)).execute()

        if not result.data:
            if raise_not_found:
                raise DailyPlanNotFoundError(str(plan_date))
            return None

        return cast(dict[str, Any], result.data[0])

    def get_or_create_for_date(self, plan_date: date) -> tuple[dict[str, Any], bool]:
        """Get existing plan or create new one for date.

        Returns:
            Tuple of (plan_dict, was_created)
        """
        existing = self.get_by_date(plan_date, raise_not_found=False)
        if existing:
            return existing, False

        new_plan = self.create(plan_date)
        return new_plan, True

    def list_all(self, limit: int = 30, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
        """List daily plans with pagination."""
        query = self.db.table(self.table).select("*", count=CountMethod.exact)
        query = query.order("date", desc=True).range(offset, offset + limit - 1)
        result = query.execute()

        plans = cast(list[dict[str, Any]], result.data or [])
        total = result.count or len(plans)

        return plans, total

    def update(self, plan_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update an existing daily plan."""
        # First verify plan exists
        self.get_by_id(plan_id)

        if not updates:
            return self.get_by_id(plan_id)

        result = self.db.table(self.table).update(updates).eq("id", plan_id).execute()

        if not result.data:
            raise DailyPlanNotFoundError(plan_id)

        return cast(dict[str, Any], result.data[0])

    def add_task_to_slot(
        self, plan_id: str, task_id: str, slot: str, current_ids: list[str]
    ) -> dict[str, Any]:
        """Add a task to a slot array."""
        updates: dict[str, Any]
        if slot == "major":
            updates = {"major_task_id": task_id}
        else:
            new_ids = [*current_ids, task_id]
            field_name = f"{slot}_task_ids"
            updates = {field_name: new_ids}

        return self.update(plan_id, updates)

    def remove_task_from_slot(
        self, plan_id: str, task_id: str, slot: str, current_ids: list[str]
    ) -> dict[str, Any]:
        """Remove a task from a slot."""
        updates: dict[str, Any]
        if slot == "major":
            updates = {"major_task_id": None}
        else:
            new_ids = [tid for tid in current_ids if tid != task_id]
            field_name = f"{slot}_task_ids"
            updates = {field_name: new_ids}

        return self.update(plan_id, updates)

    def get_tasks_by_ids(self, task_ids: list[str]) -> list[dict[str, Any]]:
        """Fetch task info for multiple task IDs."""
        if not task_ids:
            return []

        result = (
            self.db.table(self.tasks_table)
            .select("id, title, quadrant, status, pomodoro_count")
            .in_("id", task_ids)
            .execute()
        )

        return cast(list[dict[str, Any]], result.data or [])

    def find_plan_with_task(self, task_id: str) -> dict[str, Any] | None:
        """Find a plan that contains the given task in any slot."""
        # Check major_task_id
        result = self.db.table(self.table).select("*").eq("major_task_id", task_id).execute()
        if result.data:
            return cast(dict[str, Any], result.data[0])

        # Check medium_task_ids array
        result = (
            self.db.table(self.table).select("*").contains("medium_task_ids", [task_id]).execute()
        )
        if result.data:
            return cast(dict[str, Any], result.data[0])

        # Check small_task_ids array
        result = (
            self.db.table(self.table).select("*").contains("small_task_ids", [task_id]).execute()
        )
        if result.data:
            return cast(dict[str, Any], result.data[0])

        return None
