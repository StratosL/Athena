"""FastAPI routes for task management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from app.core.database import get_supabase_client
from app.features.tasks.exceptions import TaskNotFoundError
from app.features.tasks.schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from app.features.tasks.service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(
    db: Annotated[Client | None, Depends(get_supabase_client)],
) -> TaskService:
    """Dependency to get TaskService instance."""
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    return TaskService(db)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, service: TaskServiceDep) -> TaskResponse:
    """Create a new task."""
    return service.create(data)


@router.get("", response_model=TaskListResponse)
def list_tasks(
    service: TaskServiceDep,
    quadrant: Annotated[int | None, Query(ge=1, le=4)] = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> TaskListResponse:
    """List all tasks with optional filtering."""
    return service.list(quadrant=quadrant, status=status_filter, limit=limit, offset=offset)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, service: TaskServiceDep) -> TaskResponse:
    """Get a task by ID."""
    try:
        return service.get(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, data: TaskUpdate, service: TaskServiceDep) -> TaskResponse:
    """Update a task."""
    try:
        return service.update(task_id, data)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, service: TaskServiceDep) -> None:
    """Delete a task."""
    try:
        service.delete(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: str, service: TaskServiceDep) -> TaskResponse:
    """Mark a task as completed."""
    try:
        return service.complete(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e
