"""Pydantic schemas for pomodoro feature."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TimerState(StrEnum):
    """Timer state enumeration."""

    IDLE = "IDLE"
    WORK = "WORK"
    SHORT_BREAK = "SHORT_BREAK"
    LONG_BREAK = "LONG_BREAK"


class PomodoroSessionCreate(BaseModel):
    """Schema for creating a new pomodoro session."""

    task_id: str | None = Field(None, description="Optional task ID to link session")
    duration_minutes: int = Field(
        default=25, ge=1, le=90, description="Session duration in minutes"
    )


class PomodoroSessionResponse(BaseModel):
    """Schema for pomodoro session response."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str | None
    started_at: datetime
    ended_at: datetime | None
    duration_minutes: int
    completed: bool
    interrupted: bool
    created_at: datetime
    updated_at: datetime


class PomodoroSessionListResponse(BaseModel):
    """Schema for paginated session list response."""

    items: list[PomodoroSessionResponse]
    total: int


class ActiveTimerResponse(BaseModel):
    """Schema for active timer state response."""

    session: PomodoroSessionResponse | None
    state: TimerState
    remaining_seconds: int


# WebSocket message schemas (for documentation and validation)
class WSMessageType(StrEnum):
    """WebSocket message types."""

    TICK = "TICK"
    STATE_CHANGE = "STATE_CHANGE"
    SESSION_COMPLETE = "SESSION_COMPLETE"
    SESSION_STARTED = "SESSION_STARTED"
    SESSION_PAUSED = "SESSION_PAUSED"
    SESSION_STOPPED = "SESSION_STOPPED"
    ERROR = "ERROR"
    PONG = "PONG"


class WSTickMessage(BaseModel):
    """WebSocket tick message."""

    type: str = "TICK"
    remaining_seconds: int
    state: TimerState


class WSStateChangeMessage(BaseModel):
    """WebSocket state change message."""

    type: str = "STATE_CHANGE"
    old_state: TimerState
    new_state: TimerState
    remaining_seconds: int


class WSSessionCompleteMessage(BaseModel):
    """WebSocket session complete message."""

    type: str = "SESSION_COMPLETE"
    session_id: str
    completed: bool
    pomodoro_count: int
