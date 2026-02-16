"""FastAPI routes for analytics feature."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from app.core.database import get_supabase_client
from app.core.logging import get_logger
from app.features.analytics.schemas import (
    AnalyticsSummary,
    PomodoroTrendResponse,
    TaskDistributionResponse,
    TimeRange,
)
from app.features.analytics.service import AnalyticsService

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service(
    db: Annotated[Client | None, Depends(get_supabase_client)],
) -> AnalyticsService:
    """Dependency to get AnalyticsService instance."""
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    return AnalyticsService(db)


AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(
    service: AnalyticsServiceDep,
    period: Annotated[TimeRange, Query()] = TimeRange.WEEK,
) -> AnalyticsSummary:
    """Get comprehensive analytics summary.

    Returns productivity metrics, task statistics, and productivity score
    for the specified time period.
    """
    return service.get_summary(period=period)


@router.get("/pomodoro-trends", response_model=PomodoroTrendResponse)
def get_pomodoro_trends(
    service: AnalyticsServiceDep,
    period: Annotated[TimeRange, Query()] = TimeRange.WEEK,
) -> PomodoroTrendResponse:
    """Get pomodoro completion trends.

    Returns daily pomodoro counts and focus minutes for the specified period.
    """
    return service.get_pomodoro_trends(period=period)


@router.get("/task-distribution", response_model=TaskDistributionResponse)
def get_task_distribution(
    service: AnalyticsServiceDep,
) -> TaskDistributionResponse:
    """Get task distribution by Eisenhower quadrant.

    Returns task counts and completion rates for each quadrant.
    """
    return service.get_task_distribution()
