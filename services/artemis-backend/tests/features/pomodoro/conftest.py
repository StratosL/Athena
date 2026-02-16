"""Test fixtures for pomodoro feature."""

import pytest

from app.features.pomodoro.schemas import PomodoroSessionCreate


@pytest.fixture
def sample_session_data() -> PomodoroSessionCreate:
    """Sample session data for testing (no task link)."""
    return PomodoroSessionCreate(task_id=None, duration_minutes=25)


@pytest.fixture
def sample_session_with_task() -> PomodoroSessionCreate:
    """Sample session data linked to a task."""
    return PomodoroSessionCreate(task_id="test-task-id", duration_minutes=25)


@pytest.fixture
def short_session_data() -> PomodoroSessionCreate:
    """Short 5-minute session for testing."""
    return PomodoroSessionCreate(task_id=None, duration_minutes=5)
