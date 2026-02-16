"""Task repository for Supabase data access."""

from datetime import UTC, datetime

from postgrest import CountMethod
from supabase import Client

from app.core.logging import get_logger
from app.features.tasks.exceptions import TaskNotFoundError
from app.features.tasks.schemas import TaskCreate, TaskResponse, TaskUpdate

logger = get_logger(__name__)


class TaskRepository:
    """Repository for task CRUD operations with Supabase."""

    def __init__(self, db: Client) -> None:
        """Initialize repository with Supabase client."""
        self.db = db
        self.table = "tasks"

    def create(self, data: TaskCreate) -> TaskResponse:
        """Create a new task."""
        payload = data.model_dump(exclude_none=True)

        result = self.db.table(self.table).insert(payload).execute()

        if not result.data:
            raise RuntimeError("Failed to create task")

        return TaskResponse.model_validate(result.data[0])

    def get_by_id(self, task_id: str) -> TaskResponse:
        """Get a task by ID."""
        result = self.db.table(self.table).select("*").eq("id", task_id).execute()

        if not result.data:
            raise TaskNotFoundError(task_id)

        return TaskResponse.model_validate(result.data[0])

    def list_all(
        self,
        quadrant: int | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[TaskResponse], int]:
        """List tasks with optional filtering."""
        query = self.db.table(self.table).select("*", count=CountMethod.exact)

        if quadrant is not None:
            query = query.eq("quadrant", quadrant)
        if status is not None:
            query = query.eq("status", status)

        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        result = query.execute()

        tasks = [TaskResponse.model_validate(row) for row in result.data]
        total = result.count or len(tasks)

        return tasks, total

    def update(self, task_id: str, data: TaskUpdate) -> TaskResponse:
        """Update an existing task."""
        # First verify task exists
        self.get_by_id(task_id)

        payload = data.model_dump(exclude_none=True)
        if not payload:
            return self.get_by_id(task_id)

        result = self.db.table(self.table).update(payload).eq("id", task_id).execute()

        if not result.data:
            raise TaskNotFoundError(task_id)

        return TaskResponse.model_validate(result.data[0])

    def delete(self, task_id: str) -> None:
        """Delete a task by ID."""
        # First verify task exists
        self.get_by_id(task_id)

        self.db.table(self.table).delete().eq("id", task_id).execute()

    def complete(self, task_id: str) -> TaskResponse:
        """Mark a task as completed."""
        # First verify task exists
        self.get_by_id(task_id)

        now = datetime.now(UTC).isoformat()
        result = (
            self.db.table(self.table)
            .update({"status": "completed", "completed_at": now})
            .eq("id", task_id)
            .execute()
        )

        if not result.data:
            raise TaskNotFoundError(task_id)

        return TaskResponse.model_validate(result.data[0])
