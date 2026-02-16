"""Pomodoro-specific exceptions."""

from app.core.exceptions import AppException


class SessionNotFoundError(AppException):
    """Raised when a pomodoro session is not found."""

    def __init__(self, session_id: str) -> None:
        super().__init__(
            message=f"Pomodoro session '{session_id}' not found",
            code="POMODORO_SESSION_NOT_FOUND",
        )


class SessionAlreadyActiveError(AppException):
    """Raised when trying to start a session while one is already active."""

    def __init__(self) -> None:
        super().__init__(
            message="A pomodoro session is already active",
            code="POMODORO_SESSION_ALREADY_ACTIVE",
        )


class NoActiveSessionError(AppException):
    """Raised when trying to operate on an active session when none exists."""

    def __init__(self) -> None:
        super().__init__(
            message="No active pomodoro session",
            code="POMODORO_NO_ACTIVE_SESSION",
        )


class InvalidSessionStateError(AppException):
    """Raised when a session operation is invalid for the current state."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            code="POMODORO_INVALID_STATE",
        )
