"""Pomodoro repository for Supabase data access."""

from datetime import UTC, datetime
from typing import Any

from postgrest import CountMethod
from supabase import Client

from app.core.logging import get_logger
from app.features.pomodoro.exceptions import SessionNotFoundError
from app.features.pomodoro.schemas import PomodoroSessionCreate, PomodoroSessionResponse
from app.features.tasks.exceptions import TaskNotFoundError

logger = get_logger(__name__)


class PomodoroRepository:
    """Repository for pomodoro session CRUD operations with Supabase."""

    def __init__(self, db: Client) -> None:
        """Initialize repository with Supabase client."""
        self.db = db
        self.table = "pomodoro_sessions"

    def create(self, data: PomodoroSessionCreate) -> PomodoroSessionResponse:
        """Create a new pomodoro session."""
        payload: dict[str, Any] = {
            "duration_minutes": data.duration_minutes,
        }
        if data.task_id:
            payload["task_id"] = data.task_id

        result = self.db.table(self.table).insert(payload).execute()

        if not result.data:
            raise RuntimeError("Failed to create pomodoro session")

        return PomodoroSessionResponse.model_validate(result.data[0])

    def get_by_id(self, session_id: str) -> PomodoroSessionResponse:
        """Get a session by ID."""
        result = self.db.table(self.table).select("*").eq("id", session_id).execute()

        if not result.data:
            raise SessionNotFoundError(session_id)

        return PomodoroSessionResponse.model_validate(result.data[0])

    def get_active_session(self) -> PomodoroSessionResponse | None:
        """Get the currently active session (where ended_at is null)."""
        result = (
            self.db.table(self.table)
            .select("*")
            .is_("ended_at", "null")
            .order("started_at", desc=True)
            .limit(1)
            .execute()
        )

        if not result.data:
            return None

        return PomodoroSessionResponse.model_validate(result.data[0])

    def list_by_task(self, task_id: str) -> list[PomodoroSessionResponse]:
        """List all sessions for a specific task."""
        result = (
            self.db.table(self.table)
            .select("*")
            .eq("task_id", task_id)
            .order("started_at", desc=True)
            .execute()
        )

        return [PomodoroSessionResponse.model_validate(row) for row in result.data]

    def list_recent(
        self, limit: int = 10, task_id: str | None = None
    ) -> tuple[list[PomodoroSessionResponse], int]:
        """List recent sessions with optional task filter."""
        query = self.db.table(self.table).select("*", count=CountMethod.exact)

        if task_id:
            query = query.eq("task_id", task_id)

        query = query.order("started_at", desc=True).limit(limit)
        result = query.execute()

        sessions = [PomodoroSessionResponse.model_validate(row) for row in result.data]
        total = result.count or len(sessions)

        return sessions, total

    def complete_session(self, session_id: str) -> PomodoroSessionResponse:
        """Mark a session as completed."""
        # First verify session exists
        self.get_by_id(session_id)

        now = datetime.now(UTC).isoformat()
        result = (
            self.db.table(self.table)
            .update({"ended_at": now, "completed": True, "interrupted": False})
            .eq("id", session_id)
            .execute()
        )

        if not result.data:
            raise SessionNotFoundError(session_id)

        return PomodoroSessionResponse.model_validate(result.data[0])

    def interrupt_session(self, session_id: str) -> PomodoroSessionResponse:
        """Mark a session as interrupted (stopped before completion)."""
        # First verify session exists
        self.get_by_id(session_id)

        now = datetime.now(UTC).isoformat()
        result = (
            self.db.table(self.table)
            .update({"ended_at": now, "completed": False, "interrupted": True})
            .eq("id", session_id)
            .execute()
        )

        if not result.data:
            raise SessionNotFoundError(session_id)

        return PomodoroSessionResponse.model_validate(result.data[0])

    def increment_task_pomodoro_count(self, task_id: str) -> None:
        """Increment the pomodoro_count on a task atomically.

        Uses PostgreSQL RPC function to avoid race conditions in concurrent updates.
        Raises TaskNotFoundError if the task doesn't exist.
        """
        logger.info("task.pomodoro_count_increment_started", task_id=task_id)

        try:
            # Use atomic RPC function to prevent race conditions
            # The function returns the new count or NULL if task doesn't exist
            result = self.db.rpc("increment_pomodoro_count", {"p_task_id": task_id}).execute()

            # Check if task exists (function returns NULL for nonexistent tasks)
            if result.data is None:
                logger.error(
                    "task.pomodoro_count_increment_failed",
                    task_id=task_id,
                    error="Task not found",
                    exc_info=False,
                )
                raise TaskNotFoundError(task_id)

            new_count = result.data
            logger.info(
                "task.pomodoro_count_increment_completed",
                task_id=task_id,
                new_count=new_count,
            )
        except TaskNotFoundError:
            # Re-raise TaskNotFoundError as-is
            raise
        except Exception as e:
            logger.error(
                "task.pomodoro_count_increment_failed",
                task_id=task_id,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise
