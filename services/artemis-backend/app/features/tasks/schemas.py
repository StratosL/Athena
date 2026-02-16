"""Pydantic schemas for task feature."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    """Base task schema with common fields."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=2000, description="Task description")
    quadrant: int = Field(..., ge=1, le=4, description="Eisenhower quadrant (1-4)")
    due_date: datetime | None = Field(None, description="Optional due date")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    quadrant: int | None = Field(None, ge=1, le=4)
    status: str | None = Field(None, pattern="^(pending|in_progress|completed)$")
    due_date: datetime | None = None


class TaskResponse(TaskBase):
    """Schema for task response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    pomodoro_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""

    items: list[TaskResponse]
    total: int
