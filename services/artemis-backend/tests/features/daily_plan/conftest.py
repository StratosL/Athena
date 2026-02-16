"""Test fixtures for daily plan feature."""

from datetime import UTC, datetime

import pytest

from app.features.daily_plan.schemas import DailyPlanCreate, TaskAssignment


@pytest.fixture
def sample_plan_data() -> DailyPlanCreate:
    """Sample daily plan data for testing."""
    return DailyPlanCreate(date=datetime.now(UTC).date())


@pytest.fixture
def sample_major_assignment() -> TaskAssignment:
    """Sample major task assignment for testing."""
    return TaskAssignment(
        task_id="00000000-0000-0000-0000-000000000001",
        slot="major",
    )


@pytest.fixture
def sample_medium_assignment() -> TaskAssignment:
    """Sample medium task assignment for testing."""
    return TaskAssignment(
        task_id="00000000-0000-0000-0000-000000000002",
        slot="medium",
    )


@pytest.fixture
def sample_small_assignment() -> TaskAssignment:
    """Sample small task assignment for testing."""
    return TaskAssignment(
        task_id="00000000-0000-0000-0000-000000000003",
        slot="small",
    )
