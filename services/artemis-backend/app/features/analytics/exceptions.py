"""Analytics feature exceptions."""

from app.core.exceptions import AppException


class InsufficientDataError(AppException):
    """Raised when not enough data for meaningful analytics."""

    def __init__(self, metric: str, required: int, available: int) -> None:
        super().__init__(
            message=f"Insufficient data for {metric}: need {required}, have {available}",
            code="ANALYTICS_INSUFFICIENT_DATA",
        )


class InvalidDateRangeError(AppException):
    """Raised when date range is invalid."""

    def __init__(self) -> None:
        super().__init__(
            message="End date must be after start date",
            code="ANALYTICS_INVALID_DATE_RANGE",
        )
