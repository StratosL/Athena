"""Daily plan service for business logic."""

from datetime import UTC, datetime
from typing import Any

from supabase import Client

from app.core.logging import get_logger
from app.features.daily_plan.exceptions import (
    InvalidTaskError,
    SlotFullError,
    TaskAlreadyAssignedError,
    TaskNotInPlanError,
)
from app.features.daily_plan.repository import DailyPlanRepository
from app.features.daily_plan.schemas import (
    SLOT_LIMITS,
    DailyPlanCreate,
    DailyPlanListResponse,
    DailyPlanResponse,
    SlotType,
    TaskAssignment,
    TaskInfo,
)
from app.features.tasks.exceptions import TaskNotFoundError
from app.features.tasks.repository import TaskRepository

logger = get_logger(__name__)


class DailyPlanService:
    """Service layer for daily plan operations with logging."""

    def __init__(self, db: Client) -> None:
        """Initialize service with database client."""
        self.repository = DailyPlanRepository(db)
        self.task_repository = TaskRepository(db)

    def _compute_completion(self, tasks: list[dict[str, Any]]) -> tuple[bool, float, int, int]:
        """Compute completion metrics for a plan.

        Returns:
            Tuple of (is_completed, completion_rate, total_tasks, completed_count)
        """
        total_tasks = len(tasks)
        if total_tasks == 0:
            return False, 0.0, 0, 0

        completed_count = sum(1 for t in tasks if t.get("status") == "completed")
        completion_rate = (completed_count / total_tasks) * 100
        is_completed = completed_count == total_tasks

        return is_completed, completion_rate, total_tasks, completed_count

    def _build_response(self, plan: dict[str, Any]) -> DailyPlanResponse:
        """Build a DailyPlanResponse from plan dict."""
        # Collect all task IDs
        task_ids: list[str] = []
        if plan.get("major_task_id"):
            task_ids.append(plan["major_task_id"])
        task_ids.extend(plan.get("medium_task_ids") or [])
        task_ids.extend(plan.get("small_task_ids") or [])

        # Fetch all tasks
        tasks = self.repository.get_tasks_by_ids(task_ids) if task_ids else []
        tasks_by_id = {t["id"]: t for t in tasks}

        # Compute completion metrics
        completed, rate, total, done = self._compute_completion(tasks)

        # Build expanded task objects
        major_task = None
        if plan.get("major_task_id") and plan["major_task_id"] in tasks_by_id:
            major_task = TaskInfo.model_validate(tasks_by_id[plan["major_task_id"]])

        medium_tasks = [
            TaskInfo.model_validate(tasks_by_id[tid])
            for tid in (plan.get("medium_task_ids") or [])
            if tid in tasks_by_id
        ]

        small_tasks = [
            TaskInfo.model_validate(tasks_by_id[tid])
            for tid in (plan.get("small_task_ids") or [])
            if tid in tasks_by_id
        ]

        return DailyPlanResponse(
            id=plan["id"],
            date=plan["date"],
            major_task_id=plan.get("major_task_id"),
            medium_task_ids=plan.get("medium_task_ids") or [],
            small_task_ids=plan.get("small_task_ids") or [],
            created_at=plan["created_at"],
            updated_at=plan["updated_at"],
            completed=completed,
            completion_rate=rate,
            total_tasks=total,
            completed_tasks=done,
            major_task=major_task,
            medium_tasks=medium_tasks,
            small_tasks=small_tasks,
        )

    def get_today(self) -> DailyPlanResponse:
        """Get or create today's plan."""
        today = datetime.now(UTC).date()
        logger.info("daily_plan.get_today_started", date=str(today))

        try:
            plan, created = self.repository.get_or_create_for_date(today)
            action = "created" if created else "retrieved"
            logger.info(
                "daily_plan.get_today_completed",
                plan_id=plan["id"],
                action=action,
            )
            return self._build_response(plan)
        except Exception as e:
            logger.error("daily_plan.get_today_failed", error=str(e), exc_info=True)
            raise

    def create(self, data: DailyPlanCreate) -> DailyPlanResponse:
        """Create a new daily plan."""
        logger.info("daily_plan.create_started", date=str(data.date))

        try:
            plan = self.repository.create(data.date)
            logger.info("daily_plan.create_completed", plan_id=plan["id"])
            return self._build_response(plan)
        except Exception as e:
            logger.error("daily_plan.create_failed", error=str(e), exc_info=True)
            raise

    def get(self, plan_id: str) -> DailyPlanResponse:
        """Get a daily plan by ID."""
        logger.info("daily_plan.get_started", plan_id=plan_id)

        try:
            plan = self.repository.get_by_id(plan_id)
            logger.info("daily_plan.get_completed", plan_id=plan_id)
            return self._build_response(plan)
        except Exception as e:
            logger.error("daily_plan.get_failed", plan_id=plan_id, error=str(e), exc_info=True)
            raise

    def list(self, limit: int = 30, offset: int = 0) -> DailyPlanListResponse:
        """List daily plans with pagination."""
        logger.info("daily_plan.list_started", limit=limit, offset=offset)

        try:
            plans, total = self.repository.list_all(limit, offset)
            items = [self._build_response(p) for p in plans]
            logger.info("daily_plan.list_completed", count=len(items), total=total)
            return DailyPlanListResponse(items=items, total=total)
        except Exception as e:
            logger.error("daily_plan.list_failed", error=str(e), exc_info=True)
            raise

    def assign_task(self, plan_id: str, assignment: TaskAssignment) -> DailyPlanResponse:
        """Assign a task to a plan slot."""
        logger.info(
            "daily_plan.assign_task_started",
            plan_id=plan_id,
            task_id=assignment.task_id,
            slot=assignment.slot,
        )

        try:
            # Get the plan
            plan = self.repository.get_by_id(plan_id)

            # Validate task exists and is not completed
            try:
                task = self.task_repository.get_by_id(assignment.task_id)
                if task.status == "completed":
                    raise InvalidTaskError(assignment.task_id)
            except TaskNotFoundError:
                raise InvalidTaskError(assignment.task_id) from None

            # Check if task is already in another plan
            existing_plan = self.repository.find_plan_with_task(assignment.task_id)
            if existing_plan:
                raise TaskAlreadyAssignedError(assignment.task_id, str(existing_plan["date"]))

            # Check slot capacity
            slot = assignment.slot
            if slot == SlotType.MAJOR:
                if plan.get("major_task_id"):
                    raise SlotFullError(slot, SLOT_LIMITS[slot])
                current_ids: list[str] = []
            elif slot == SlotType.MEDIUM:
                current_ids = plan.get("medium_task_ids") or []
                if len(current_ids) >= SLOT_LIMITS[slot]:
                    raise SlotFullError(slot, SLOT_LIMITS[slot])
            else:  # small
                current_ids = plan.get("small_task_ids") or []
                if len(current_ids) >= SLOT_LIMITS[slot]:
                    raise SlotFullError(slot, SLOT_LIMITS[slot])

            # Add task to slot
            updated_plan = self.repository.add_task_to_slot(
                plan_id, assignment.task_id, slot, current_ids
            )

            logger.info(
                "daily_plan.assign_task_completed",
                plan_id=plan_id,
                task_id=assignment.task_id,
                slot=slot,
            )
            return self._build_response(updated_plan)

        except Exception as e:
            logger.error(
                "daily_plan.assign_task_failed",
                plan_id=plan_id,
                task_id=assignment.task_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def remove_task(self, plan_id: str, task_id: str) -> DailyPlanResponse:
        """Remove a task from a plan."""
        logger.info("daily_plan.remove_task_started", plan_id=plan_id, task_id=task_id)

        try:
            plan = self.repository.get_by_id(plan_id)

            # Find which slot contains the task
            slot: str | None = None
            current_ids: list[str] = []

            if plan.get("major_task_id") == task_id:
                slot = SlotType.MAJOR
            elif task_id in (plan.get("medium_task_ids") or []):
                slot = SlotType.MEDIUM
                current_ids = plan.get("medium_task_ids") or []
            elif task_id in (plan.get("small_task_ids") or []):
                slot = SlotType.SMALL
                current_ids = plan.get("small_task_ids") or []

            if not slot:
                raise TaskNotInPlanError(task_id)

            # Remove task from slot
            updated_plan = self.repository.remove_task_from_slot(
                plan_id, task_id, slot, current_ids
            )

            logger.info(
                "daily_plan.remove_task_completed",
                plan_id=plan_id,
                task_id=task_id,
                slot=slot,
            )
            return self._build_response(updated_plan)

        except Exception as e:
            logger.error(
                "daily_plan.remove_task_failed",
                plan_id=plan_id,
                task_id=task_id,
                error=str(e),
                exc_info=True,
            )
            raise
