"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import close_supabase, init_supabase
from app.core.logging import get_logger, setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.features.analytics import router as analytics_router
from app.features.daily_plan import router as daily_plan_router
from app.features.pomodoro import router as pomodoro_router
from app.features.tasks import router as tasks_router
from app.shared.schemas import HealthResponse

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events for startup and shutdown."""
    # Startup
    setup_logging()
    logger.info(
        "application.lifecycle.started",
        app_name=settings.app_name,
        version=settings.version,
        debug=settings.debug,
    )

    # Initialize database
    init_supabase()

    yield

    # Shutdown
    close_supabase()
    logger.info("application.lifecycle.stopped", app_name=settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns application status, version, and database connectivity.
    """
    from app.core.database import get_supabase_client

    db_client = get_supabase_client()
    db_status = "connected" if db_client is not None else "not configured"

    return HealthResponse(
        status="healthy",
        version=settings.version,
        database=db_status,
    )


# Register feature routers
app.include_router(tasks_router)
app.include_router(daily_plan_router)
app.include_router(pomodoro_router)
app.include_router(analytics_router)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    """Root endpoint returning application info."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
    }
