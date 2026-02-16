"""Pomodoro service for business logic."""

from datetime import UTC, datetime

from supabase import Client

from app.core.logging import get_logger
from app.features.pomodoro.exceptions import NoActiveSessionError, SessionAlreadyActiveError
from app.features.pomodoro.repository import PomodoroRepository
from app.features.pomodoro.schemas import (
    ActiveTimerResponse,
    PomodoroSessionCreate,
    PomodoroSessionListResponse,
    PomodoroSessionResponse,
    TimerState,
)

logger = get_logger(__name__)

# Timer durations in seconds
WORK_DURATION = 25 * 60  # 25 minutes
SHORT_BREAK_DURATION = 5 * 60  # 5 minutes
LONG_BREAK_DURATION = 15 * 60  # 15 minutes
POMODOROS_BEFORE_LONG_BREAK = 4


class PomodoroService:
    """Service layer for pomodoro operations with logging."""

    def __init__(self, db: Client) -> None:
        """Initialize service with database client."""
        self.repository = PomodoroRepository(db)

    def start_session(self, task_id: str | None = None) -> PomodoroSessionResponse:
        """Start a new pomodoro session."""
        logger.info("pomodoro.session_start_requested", task_id=task_id)

        try:
            # Check if there's already an active session
            active = self.repository.get_active_session()
            if active:
                logger.warning(
                    "pomodoro.session_start_rejected",
                    reason="active_session_exists",
                    active_session_id=active.id,
                )
                raise SessionAlreadyActiveError()

            # Create new session
            data = PomodoroSessionCreate(task_id=task_id, duration_minutes=25)
            session = self.repository.create(data)

            logger.info(
                "pomodoro.session_started",
                session_id=session.id,
                task_id=task_id,
                duration_minutes=25,
            )
            return session

        except SessionAlreadyActiveError:
            raise
        except Exception as e:
            logger.error("pomodoro.session_start_failed", error=str(e), exc_info=True)
            raise

    def get_active(self) -> ActiveTimerResponse:
        """Get the currently active timer state."""
        logger.info("pomodoro.active_timer_requested")

        try:
            session = self.repository.get_active_session()

            if not session:
                logger.info("pomodoro.no_active_session")
                return ActiveTimerResponse(
                    session=None,
                    state=TimerState.IDLE,
                    remaining_seconds=0,
                )

            # Calculate remaining seconds
            now = datetime.now(UTC)
            elapsed = (now - session.started_at).total_seconds()
            total_seconds = session.duration_minutes * 60
            remaining = max(0, int(total_seconds - elapsed))

            logger.info(
                "pomodoro.active_timer_retrieved",
                session_id=session.id,
                remaining_seconds=remaining,
            )

            return ActiveTimerResponse(
                session=session,
                state=TimerState.WORK,
                remaining_seconds=remaining,
            )

        except Exception as e:
            logger.error("pomodoro.active_timer_failed", error=str(e), exc_info=True)
            raise

    def stop_session(self) -> PomodoroSessionResponse:
        """Stop the active session (mark as interrupted)."""
        logger.info("pomodoro.session_stop_requested")

        try:
            session = self.repository.get_active_session()
            if not session:
                logger.warning("pomodoro.session_stop_rejected", reason="no_active_session")
                raise NoActiveSessionError()

            stopped = self.repository.interrupt_session(session.id)

            logger.info(
                "pomodoro.session_stopped",
                session_id=stopped.id,
                interrupted=True,
            )
            return stopped

        except NoActiveSessionError:
            raise
        except Exception as e:
            logger.error("pomodoro.session_stop_failed", error=str(e), exc_info=True)
            raise

    def complete_session(self) -> PomodoroSessionResponse:
        """Complete the active session and update task pomodoro count."""
        logger.info("pomodoro.session_complete_requested")

        try:
            session = self.repository.get_active_session()
            if not session:
                logger.warning("pomodoro.session_complete_rejected", reason="no_active_session")
                raise NoActiveSessionError()

            completed = self.repository.complete_session(session.id)

            # Increment task's pomodoro count if linked to a task
            if completed.task_id:
                self.repository.increment_task_pomodoro_count(completed.task_id)
                logger.info(
                    "pomodoro.task_pomodoro_count_incremented",
                    task_id=completed.task_id,
                )

            logger.info(
                "pomodoro.session_completed",
                session_id=completed.id,
                task_id=completed.task_id,
                duration_minutes=completed.duration_minutes,
            )
            return completed

        except NoActiveSessionError:
            raise
        except Exception as e:
            logger.error("pomodoro.session_complete_failed", error=str(e), exc_info=True)
            raise

    def get_session(self, session_id: str) -> PomodoroSessionResponse:
        """Get a specific session by ID."""
        logger.info("pomodoro.session_get_requested", session_id=session_id)

        try:
            session = self.repository.get_by_id(session_id)
            logger.info("pomodoro.session_get_completed", session_id=session_id)
            return session
        except Exception as e:
            logger.error(
                "pomodoro.session_get_failed",
                session_id=session_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def list_sessions(
        self, task_id: str | None = None, limit: int = 10
    ) -> PomodoroSessionListResponse:
        """List recent pomodoro sessions."""
        logger.info("pomodoro.sessions_list_requested", task_id=task_id, limit=limit)

        try:
            sessions, total = self.repository.list_recent(limit=limit, task_id=task_id)
            logger.info(
                "pomodoro.sessions_list_completed",
                count=len(sessions),
                total=total,
            )
            return PomodoroSessionListResponse(items=sessions, total=total)
        except Exception as e:
            logger.error("pomodoro.sessions_list_failed", error=str(e), exc_info=True)
            raise
