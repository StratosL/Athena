"""Agent dependencies for Hierarchical RAG.

Reference: examples/dependencies.py - Adapted for OpenRouter embeddings.

This module provides the AgentDependencies dataclass that is injected
into all agent tools, providing access to database and embedding services.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import asyncpg
from openai import AsyncOpenAI
from pgvector.asyncpg import register_vector

from ..settings import load_settings

logger = logging.getLogger(__name__)


@dataclass
class AgentDependencies:
    """Dependencies injected into the agent and available in all tools.

    Reference: examples/dependencies.py:10-70

    This class manages:
    - Database connection pool
    - Embedding client (via OpenRouter)
    - Settings
    - Category cache for efficient lookups
    """

    # Core dependencies
    db_pool: Optional[asyncpg.Pool] = None
    embedding_client: Optional[AsyncOpenAI] = None
    settings: Optional[Any] = None

    # Cache for category tree (for efficient lookups)
    category_cache: Dict[str, Any] = field(default_factory=dict)

    async def initialize(self) -> None:
        """Initialize external connections.

        Performs lazy initialization of database pool and embedding client.
        """
        if not self.settings:
            self.settings = load_settings()

        # Initialize database pool
        if not self.db_pool:
            logger.info("Initializing database pool...")
            self.db_pool = await asyncpg.create_pool(
                self.settings.database_url,
                min_size=self.settings.db_pool_min_size,
                max_size=self.settings.db_pool_max_size,
                init=self._init_connection
            )
            logger.info("Database pool initialized")

        # Initialize OpenRouter client for embeddings
        # Uses same API key as LLM - single key for everything!
        if not self.embedding_client:
            logger.info("Initializing embedding client...")
            self.embedding_client = AsyncOpenAI(
                api_key=self.settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            logger.info("Embedding client initialized")

    async def _init_connection(self, conn: asyncpg.Connection) -> None:
        """Initialize pgvector on each database connection.

        Args:
            conn: Database connection to initialize.
        """
        await register_vector(conn)

    async def cleanup(self) -> None:
        """Clean up external connections."""
        if self.db_pool:
            logger.info("Closing database pool...")
            await self.db_pool.close()
            self.db_pool = None
            logger.info("Database pool closed")

        # Clear caches
        self.category_cache.clear()

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text via OpenRouter.

        Reference: examples/dependencies.py:50-60

        Args:
            text: Text to generate embedding for.

        Returns:
            Embedding vector as list of floats.
        """
        if not self.embedding_client:
            await self.initialize()

        response = await self.embedding_client.embeddings.create(
            model=self.settings.embedding_model,  # "openai/text-embedding-3-small"
            input=text
        )
        return response.data[0].embedding

    def get_embedding_str(self, embedding: List[float]) -> str:
        """Convert embedding to PostgreSQL vector string format.

        Reference: examples/tools.py:52-53

        Args:
            embedding: Embedding vector.

        Returns:
            PostgreSQL vector string format: '[1.0,2.0,3.0]'
        """
        return '[' + ','.join(map(str, embedding)) + ']'


async def create_dependencies() -> AgentDependencies:
    """Create and initialize agent dependencies.

    Returns:
        Initialized AgentDependencies instance.
    """
    deps = AgentDependencies()
    await deps.initialize()
    return deps
