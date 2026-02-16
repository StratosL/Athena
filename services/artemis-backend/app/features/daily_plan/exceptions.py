"""Daily plan specific exceptions."""

from app.core.exceptions import AppException


class DailyPlanNotFoundError(AppException):
    """Raised when a daily plan is not found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(
            message=f"Daily plan '{identifier}' not found",
            code="DAILY_PLAN_NOT_FOUND",
        )


class DailyPlanExistsError(AppException):
    """Raised when a daily plan already exists for a date."""

    def __init__(self, date: str) -> None:
        super().__init__(
            message=f"Daily plan already exists for date '{date}'",
            code="DAILY_PLAN_EXISTS",
        )


class SlotFullError(AppException):
    """Raised when a slot is at capacity."""

    def __init__(self, slot: str, limit: int) -> None:
        super().__init__(
            message=f"Slot '{slot}' is full (max {limit} tasks)",
            code="SLOT_FULL",
        )


class TaskAlreadyAssignedError(AppException):
    """Raised when a task is already assigned to a plan."""

    def __init__(self, task_id: str, plan_date: str) -> None:
        super().__init__(
            message=f"Task '{task_id}' is already assigned to plan for '{plan_date}'",
            code="TASK_ALREADY_ASSIGNED",
        )


class TaskNotInPlanError(AppException):
    """Raised when a task is not found in a plan."""

    def __init__(self, task_id: str) -> None:
        super().__init__(
            message=f"Task '{task_id}' is not in this plan",
            code="TASK_NOT_IN_PLAN",
        )


class InvalidTaskError(AppException):
    """Raised when a task cannot be assigned (e.g., completed or not found)."""

    def __init__(self, task_id: str) -> None:
        super().__init__(
            message=f"Task '{task_id}' is invalid or cannot be assigned",
            code="INVALID_TASK",
        )
