"""FastAPI routes for pomodoro timer."""

import asyncio
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from supabase import Client

from app.core.database import get_supabase_client
from app.core.logging import get_logger
from app.features.pomodoro.exceptions import (
    NoActiveSessionError,
    SessionAlreadyActiveError,
    SessionNotFoundError,
)
from app.features.pomodoro.manager import timer_manager
from app.features.pomodoro.schemas import (
    ActiveTimerResponse,
    PomodoroSessionCreate,
    PomodoroSessionListResponse,
    PomodoroSessionResponse,
)
from app.features.pomodoro.service import PomodoroService

logger = get_logger(__name__)

router = APIRouter(prefix="/pomodoro", tags=["pomodoro"])


def get_pomodoro_service(
    db: Annotated[Client | None, Depends(get_supabase_client)],
) -> PomodoroService:
    """Dependency to get PomodoroService instance."""
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not configured",
        )
    return PomodoroService(db)


PomodoroServiceDep = Annotated[PomodoroService, Depends(get_pomodoro_service)]


@router.get("/active", response_model=ActiveTimerResponse)
def get_active_timer(service: PomodoroServiceDep) -> ActiveTimerResponse:
    """Get the current active timer state."""
    return service.get_active()


@router.post("/start", response_model=PomodoroSessionResponse, status_code=status.HTTP_201_CREATED)
def start_session(
    service: PomodoroServiceDep,
    data: PomodoroSessionCreate | None = None,
) -> PomodoroSessionResponse:
    """Start a new pomodoro session."""
    try:
        task_id = data.task_id if data else None
        return service.start_session(task_id)
    except SessionAlreadyActiveError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message) from e


@router.post("/stop", response_model=PomodoroSessionResponse)
def stop_session(service: PomodoroServiceDep) -> PomodoroSessionResponse:
    """Stop and discard the current session."""
    try:
        return service.stop_session()
    except NoActiveSessionError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.post("/complete", response_model=PomodoroSessionResponse)
def complete_session(service: PomodoroServiceDep) -> PomodoroSessionResponse:
    """Complete the current session successfully."""
    try:
        return service.complete_session()
    except NoActiveSessionError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.get("/sessions", response_model=PomodoroSessionListResponse)
def list_sessions(
    service: PomodoroServiceDep,
    task_id: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> PomodoroSessionListResponse:
    """List recent pomodoro sessions."""
    return service.list_sessions(task_id=task_id, limit=limit)


@router.get("/sessions/{session_id}", response_model=PomodoroSessionResponse)
def get_session(session_id: str, service: PomodoroServiceDep) -> PomodoroSessionResponse:
    """Get a specific session by ID."""
    try:
        return service.get_session(session_id)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.websocket("/ws/{session_id}")
async def websocket_timer(
    websocket: WebSocket,
    session_id: str,
    db: Annotated[Client | None, Depends(get_supabase_client)],
) -> None:
    """WebSocket endpoint for real-time timer updates.

    Messages from client:
    - {"type": "PING"} - Keepalive ping
    - {"type": "STOP"} - Request to stop session

    Messages to client:
    - {"type": "TICK", "remaining_seconds": int, "state": str}
    - {"type": "SESSION_COMPLETE", "session_id": str}
    - {"type": "PONG"}
    - {"type": "ERROR", "message": str}
    """
    if db is None:
        await websocket.close(code=1011, reason="Database not configured")
        return

    service = PomodoroService(db)
    await timer_manager.connect(websocket, session_id)

    try:
        # Start tick loop in background
        tick_task = asyncio.create_task(_tick_loop(websocket, session_id, service))

        try:
            while True:
                data = await websocket.receive_json()
                await _handle_client_message(data, websocket, session_id, service)
        except WebSocketDisconnect:
            logger.info("pomodoro.websocket.client_disconnected", session_id=session_id)
        finally:
            tick_task.cancel()
            try:
                await tick_task
            except asyncio.CancelledError:
                pass

    finally:
        await timer_manager.disconnect(websocket, session_id)


async def _tick_loop(
    websocket: WebSocket,
    session_id: str,
    service: PomodoroService,
) -> None:
    """Send tick updates every second while session is active."""
    try:
        while True:
            try:
                active = service.get_active()

                if active.session is None or active.session.id != session_id:
                    # Session ended or different session
                    await timer_manager.send_personal(
                        {
                            "type": "SESSION_COMPLETE",
                            "session_id": session_id,
                            "completed": active.session is None,
                        },
                        websocket,
                    )
                    break

                if active.remaining_seconds <= 0:
                    # Timer finished - auto-complete
                    service.complete_session()
                    await timer_manager.broadcast_to_session(
                        session_id,
                        {
                            "type": "SESSION_COMPLETE",
                            "session_id": session_id,
                            "completed": True,
                        },
                    )
                    break

                # Send tick update
                await timer_manager.send_personal(
                    {
                        "type": "TICK",
                        "remaining_seconds": active.remaining_seconds,
                        "state": active.state.value,
                    },
                    websocket,
                )

            except Exception as e:
                logger.error(
                    "pomodoro.websocket.tick_error",
                    session_id=session_id,
                    error=str(e),
                    exc_info=True,
                )

            await asyncio.sleep(1)

    except asyncio.CancelledError:
        pass


async def _handle_client_message(
    data: dict[str, Any],
    websocket: WebSocket,
    session_id: str,
    service: PomodoroService,
) -> None:
    """Handle incoming WebSocket messages from client."""
    msg_type = data.get("type", "").upper()

    if msg_type == "PING":
        await timer_manager.send_personal({"type": "PONG"}, websocket)

    elif msg_type == "STOP":
        try:
            service.stop_session()
            await timer_manager.broadcast_to_session(
                session_id,
                {"type": "SESSION_STOPPED", "session_id": session_id},
            )
        except NoActiveSessionError:
            await timer_manager.send_personal(
                {"type": "ERROR", "message": "No active session"},
                websocket,
            )

    else:
        await timer_manager.send_personal(
            {"type": "ERROR", "message": f"Unknown message type: {msg_type}"},
            websocket,
        )
