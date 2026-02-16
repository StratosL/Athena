"""Pydantic schemas for daily plan feature."""

import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SlotType:
    """Slot type constants for daily plans."""

    MAJOR = "major"
    MEDIUM = "medium"
    SMALL = "small"


SLOT_LIMITS = {
    SlotType.MAJOR: 1,
    SlotType.MEDIUM: 3,
    SlotType.SMALL: 5,
}


class DailyPlanCreate(BaseModel):
    """Schema for creating a new daily plan."""

    date: datetime.date = Field(..., description="Date for the daily plan")


class TaskAssignment(BaseModel):
    """Schema for assigning a task to a slot."""

    task_id: str = Field(..., description="Task ID to assign")
    slot: str = Field(
        ...,
        description="Slot type (major, medium, small)",
        pattern="^(major|medium|small)$",
    )

    @field_validator("slot")
    @classmethod
    def validate_slot(cls, v: str) -> str:
        """Validate slot type."""
        if v not in [SlotType.MAJOR, SlotType.MEDIUM, SlotType.SMALL]:
            raise ValueError("Slot must be 'major', 'medium', or 'small'")
        return v


class TaskInfo(BaseModel):
    """Schema for task information in daily plan responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    quadrant: int
    status: str
    pomodoro_count: int


class DailyPlanResponse(BaseModel):
    """Schema for daily plan response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    date: datetime.date
    major_task_id: str | None = None
    medium_task_ids: list[str] = Field(default_factory=list)
    small_task_ids: list[str] = Field(default_factory=list)
    created_at: datetime.datetime
    updated_at: datetime.datetime

    # Computed fields
    completed: bool = False
    completion_rate: float = 0.0
    total_tasks: int = 0
    completed_tasks: int = 0

    # Expanded task objects
    major_task: TaskInfo | None = None
    medium_tasks: list[TaskInfo] = Field(default_factory=list)
    small_tasks: list[TaskInfo] = Field(default_factory=list)


class DailyPlanListResponse(BaseModel):
    """Schema for paginated daily plan list response."""

    items: list[DailyPlanResponse]
    total: int
