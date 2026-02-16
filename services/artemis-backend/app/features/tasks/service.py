"""Task service for business logic."""

from supabase import Client

from app.core.logging import get_logger
from app.features.tasks.repository import TaskRepository
from app.features.tasks.schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate

logger = get_logger(__name__)


class TaskService:
    """Service layer for task operations with logging."""

    def __init__(self, db: Client) -> None:
        """Initialize service with database client."""
        self.repository = TaskRepository(db)

    def create(self, data: TaskCreate) -> TaskResponse:
        """Create a new task."""
        logger.info("task.create_started", title=data.title, quadrant=data.quadrant)

        try:
            task = self.repository.create(data)
            logger.info("task.create_completed", task_id=task.id, quadrant=task.quadrant)
            return task
        except Exception as e:
            logger.error("task.create_failed", error=str(e), exc_info=True)
            raise

    def get(self, task_id: str) -> TaskResponse:
        """Get a task by ID."""
        logger.info("task.get_started", task_id=task_id)

        try:
            task = self.repository.get_by_id(task_id)
            logger.info("task.get_completed", task_id=task_id)
            return task
        except Exception as e:
            logger.error("task.get_failed", task_id=task_id, error=str(e), exc_info=True)
            raise

    def list(
        self,
        quadrant: int | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> TaskListResponse:
        """List tasks with optional filtering."""
        logger.info("task.list_started", quadrant=quadrant, status=status)

        try:
            tasks, total = self.repository.list_all(quadrant, status, limit, offset)
            logger.info("task.list_completed", count=len(tasks), total=total)
            return TaskListResponse(items=tasks, total=total)
        except Exception as e:
            logger.error("task.list_failed", error=str(e), exc_info=True)
            raise

    def update(self, task_id: str, data: TaskUpdate) -> TaskResponse:
        """Update an existing task."""
        logger.info("task.update_started", task_id=task_id)

        try:
            task = self.repository.update(task_id, data)
            logger.info("task.update_completed", task_id=task_id)
            return task
        except Exception as e:
            logger.error("task.update_failed", task_id=task_id, error=str(e), exc_info=True)
            raise

    def delete(self, task_id: str) -> None:
        """Delete a task."""
        logger.info("task.delete_started", task_id=task_id)

        try:
            self.repository.delete(task_id)
            logger.info("task.delete_completed", task_id=task_id)
        except Exception as e:
            logger.error("task.delete_failed", task_id=task_id, error=str(e), exc_info=True)
            raise

    def complete(self, task_id: str) -> TaskResponse:
        """Mark a task as completed."""
        logger.info("task.complete_started", task_id=task_id)

        try:
            task = self.repository.complete(task_id)
            logger.info("task.complete_completed", task_id=task_id)
            return task
        except Exception as e:
            logger.error("task.complete_failed", task_id=task_id, error=str(e), exc_info=True)
            raise
