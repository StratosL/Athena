"""Database connection management for Hierarchical RAG Workshop.

Reference: examples/dependencies.py:29-35 for pool pattern.
"""

import logging
import asyncpg
from pgvector.asyncpg import register_vector

from ..settings import load_settings

logger = logging.getLogger(__name__)

# Global pool (singleton pattern)
_pool: asyncpg.Pool | None = None
_pgvector_enabled: bool = False


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Initialize each connection with pgvector support.

    This callback is called for each new connection in the pool.

    Args:
        conn: The database connection to initialize.
    """
    global _pgvector_enabled
    if _pgvector_enabled:
        await register_vector(conn)


async def get_pool(with_pgvector: bool = True) -> asyncpg.Pool:
    """Get or create the database connection pool.

    Args:
        with_pgvector: Whether to register pgvector on connections.

    Returns:
        Database connection pool.
    """
    global _pool, _pgvector_enabled
    if _pool is None:
        settings = load_settings()
        logger.info("Creating database connection pool...")

        # Set the pgvector flag before creating pool
        _pgvector_enabled = with_pgvector

        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
            init=_init_connection if with_pgvector else None
        )
        logger.info(
            f"Database pool created (min={settings.db_pool_min_size}, "
            f"max={settings.db_pool_max_size})"
        )
    return _pool


async def close_pool() -> None:
    """Close the database connection pool."""
    global _pool, _pgvector_enabled
    if _pool:
        logger.info("Closing database connection pool...")
        await _pool.close()
        _pool = None
        _pgvector_enabled = False
        logger.info("Database pool closed")


async def test_connection() -> bool:
    """Test the database connection (without pgvector).

    Returns:
        True if connection is successful, False otherwise.
    """
    settings = load_settings()
    try:
        # Test with a simple connection without pgvector
        conn = await asyncpg.connect(settings.database_url)
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        return result == 1
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def enable_pgvector() -> bool:
    """Enable pgvector extension and recreate pool with vector support.

    Returns:
        True if pgvector is enabled, False otherwise.
    """
    global _pool, _pgvector_enabled

    settings = load_settings()

    try:
        # Connect and enable extension
        conn = await asyncpg.connect(settings.database_url)
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.close()
        logger.info("pgvector extension enabled")

        # Close existing pool if any
        if _pool:
            await _pool.close()
            _pool = None

        # Create new pool with pgvector support
        _pgvector_enabled = True
        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
            init=_init_connection
        )

        return True
    except Exception as e:
        logger.error(f"Failed to enable pgvector: {e}")
        return False
