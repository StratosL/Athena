"""Common Pydantic schemas shared across feature slices."""

from typing import Any

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Standard pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size


class PaginatedResponse[T](BaseModel):
    """Standard paginated response format."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    version: str
    database: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str
    code: str | None = None
    details: dict[str, Any] | None = None
