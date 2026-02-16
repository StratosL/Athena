"""Base exception classes for the application."""


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class ConfigurationError(AppException):
    """Raised when application configuration is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFIGURATION_ERROR")


class DatabaseError(AppException):
    """Raised when database operations fail."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="DATABASE_ERROR")


class NotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: str) -> None:
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, code="NOT_FOUND")


class ValidationError(AppException):
    """Raised when input validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="VALIDATION_ERROR")
