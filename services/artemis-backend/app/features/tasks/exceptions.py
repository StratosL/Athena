"""Task-specific exceptions."""

from app.core.exceptions import AppException


class TaskNotFoundError(AppException):
    """Raised when a task is not found."""

    def __init__(self, task_id: str) -> None:
        super().__init__(message=f"Task '{task_id}' not found", code="TASK_NOT_FOUND")


class TaskValidationError(AppException):
    """Raised when task data validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="TASK_VALIDATION_ERROR")
