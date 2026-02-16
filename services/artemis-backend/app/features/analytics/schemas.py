"""Pydantic schemas for analytics feature."""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TimeRange(StrEnum):
    """Time range options for analytics."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"


# Response schemas
class PomodoroTrendPoint(BaseModel):
    """Single data point for pomodoro trend."""

    date: str = Field(..., description="ISO date string")
    count: int = Field(..., ge=0, description="Number of completed pomodoros")
    total_minutes: int = Field(..., ge=0, description="Total focus minutes")


class PomodoroTrendResponse(BaseModel):
    """Response for pomodoro trend data."""

    model_config = ConfigDict(from_attributes=True)

    period: TimeRange
    data_points: list[PomodoroTrendPoint]
    total_pomodoros: int
    total_minutes: int
    average_per_day: float


class TaskQuadrantStats(BaseModel):
    """Task statistics for a single quadrant."""

    quadrant: int = Field(..., ge=1, le=4)
    total: int
    completed: int
    completion_rate: float


class TaskDistributionResponse(BaseModel):
    """Response for task distribution by quadrant."""

    model_config = ConfigDict(from_attributes=True)

    quadrants: list[TaskQuadrantStats]
    total_tasks: int
    total_completed: int
    overall_completion_rate: float


class DailyPlanStats(BaseModel):
    """Statistics for daily plan completion."""

    total_plans: int
    plans_completed: int
    average_completion_rate: float
    tasks_planned: int
    tasks_completed: int


class ProductivityScore(BaseModel):
    """Computed productivity score with breakdown."""

    score: int = Field(..., ge=0, le=100, description="Overall productivity score 0-100")
    components: dict[str, float] = Field(..., description="Score component breakdown")
    trend: str = Field(..., description="Trend direction: up, down, stable")
    trend_percentage: float = Field(..., description="Percentage change from previous period")


class AnalyticsSummary(BaseModel):
    """Comprehensive analytics summary."""

    model_config = ConfigDict(from_attributes=True)

    # Period info
    period: TimeRange
    start_date: date
    end_date: date

    # Pomodoro stats
    total_pomodoros: int
    total_focus_minutes: int
    average_pomodoros_per_day: float

    # Task stats
    tasks_created: int
    tasks_completed: int
    task_completion_rate: float

    # Daily plan stats
    daily_plan_stats: DailyPlanStats

    # Productivity score
    productivity_score: ProductivityScore
