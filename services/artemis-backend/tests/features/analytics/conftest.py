"""Test fixtures for analytics feature."""

import pytest

from app.features.analytics.schemas import TimeRange


@pytest.fixture
def week_period() -> TimeRange:
    """Week time range for testing."""
    return TimeRange.WEEK


@pytest.fixture
def month_period() -> TimeRange:
    """Month time range for testing."""
    return TimeRange.MONTH
