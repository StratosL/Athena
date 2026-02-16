"""Supabase database client configuration.

The Supabase client is initialized during application startup
and accessed via FastAPI's dependency injection.
"""

from supabase import Client, create_client

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Global client instance (set during app startup)
_supabase_client: Client | None = None


def init_supabase() -> Client | None:
    """Initialize the Supabase client.

    Should be called once during application startup.
    """
    global _supabase_client

    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_anon_key:
        logger.warning(
            "database.connection_skipped",
            reason="Missing SUPABASE_URL or SUPABASE_ANON_KEY",
        )
        return None

    _supabase_client = create_client(
        settings.supabase_url,
        settings.supabase_anon_key,
    )

    logger.info(
        "database.connection_initialized",
        provider="supabase",
        url=settings.supabase_url[:30] + "...",
    )

    return _supabase_client


def get_supabase_client() -> Client | None:
    """Get the Supabase client instance.

    Returns None if client not initialized (e.g., missing credentials).
    """
    return _supabase_client


def close_supabase() -> None:
    """Close the Supabase client connection.

    Called during application shutdown.
    """
    global _supabase_client

    if _supabase_client is not None:
        # Supabase client doesn't have explicit close, but we clear reference
        _supabase_client = None
        logger.info("database.connection_closed", provider="supabase")
