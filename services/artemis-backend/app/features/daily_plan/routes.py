"""FastAPI routes for daily plan management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from app.core.database import get_supabase_client
from app.features.daily_plan.exceptions import (
    DailyPlanExistsError,
    DailyPlanNotFoundError,
    InvalidTaskError,
    SlotFullError,
    TaskAlreadyAssignedError,
    TaskNotInPlanError,
)
from app.features.daily_plan.schemas import (
    DailyPlanCreate,
    DailyPlanListResponse,
    DailyPlanResponse,
    TaskAssignment,
)
from app.features.daily_plan.service import DailyPlanService

router = APIRouter(prefix="/daily-plans", tags=["daily-plans"])


def get_daily_plan_service(
    db: Annotated[Client | None, Depends(get_supabase_client)],
) -> DailyPlanService:
    """Dependency to get DailyPlanService instance."""
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    return DailyPlanService(db)


DailyPlanServiceDep = Annotated[DailyPlanService, Depends(get_daily_plan_service)]


@router.get("/today", response_model=DailyPlanResponse)
def get_today_plan(service: DailyPlanServiceDep) -> DailyPlanResponse:
    """Get or create today's daily plan."""
    return service.get_today()


@router.post("", response_model=DailyPlanResponse, status_code=status.HTTP_201_CREATED)
def create_daily_plan(data: DailyPlanCreate, service: DailyPlanServiceDep) -> DailyPlanResponse:
    """Create a new daily plan for a specific date."""
    try:
        return service.create(data)
    except DailyPlanExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message) from e


@router.get("", response_model=DailyPlanListResponse)
def list_daily_plans(
    service: DailyPlanServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> DailyPlanListResponse:
    """List all daily plans with pagination."""
    return service.list(limit=limit, offset=offset)


@router.get("/{plan_id}", response_model=DailyPlanResponse)
def get_daily_plan(plan_id: str, service: DailyPlanServiceDep) -> DailyPlanResponse:
    """Get a daily plan by ID."""
    try:
        return service.get(plan_id)
    except DailyPlanNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.post("/{plan_id}/tasks", response_model=DailyPlanResponse)
def assign_task_to_plan(
    plan_id: str, assignment: TaskAssignment, service: DailyPlanServiceDep
) -> DailyPlanResponse:
    """Assign a task to a daily plan slot."""
    try:
        return service.assign_task(plan_id, assignment)
    except DailyPlanNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except (DailyPlanExistsError, TaskAlreadyAssignedError) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message) from e
    except InvalidTaskError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e
    except SlotFullError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e


@router.delete("/{plan_id}/tasks/{task_id}", response_model=DailyPlanResponse)
def remove_task_from_plan(
    plan_id: str, task_id: str, service: DailyPlanServiceDep
) -> DailyPlanResponse:
    """Remove a task from a daily plan."""
    try:
        return service.remove_task(plan_id, task_id)
    except DailyPlanNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
    except TaskNotInPlanError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
