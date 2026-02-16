"""Test fixtures for task feature."""

import pytest

from app.features.tasks.schemas import TaskCreate


@pytest.fixture
def sample_task_data() -> TaskCreate:
    """Sample task data for testing."""
    return TaskCreate(
        title="Test Task",
        description="A test task description",
        quadrant=1,
    )


@pytest.fixture
def sample_task_data_q2() -> TaskCreate:
    """Sample Q2 task data for testing."""
    return TaskCreate(
        title="Important but not urgent",
        description="Schedule this for later",
        quadrant=2,
    )
