"""Settings configuration for Hierarchical RAG Workshop.

Reference: examples/settings.py - Adapted with native OpenRouter support.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database Configuration
    database_url: str = Field(
        ...,
        description="PostgreSQL connection URL with PGVector extension"
    )
    db_pool_min_size: int = Field(
        default=2,
        description="Minimum database connection pool size"
    )
    db_pool_max_size: int = Field(
        default=10,
        description="Maximum database connection pool size"
    )

    # OpenRouter Configuration - SINGLE KEY FOR LLM + EMBEDDINGS
    openrouter_api_key: str = Field(
        ...,
        description="OpenRouter API key (used for both LLM and embeddings)"
    )

    # LLM Configuration - NATIVE OPENROUTER
    llm_model: str = Field(
        default="anthropic/claude-3-5-haiku-20241022",
        description="OpenRouter model name for LLM"
    )

    # Embedding Configuration - VIA OPENROUTER
    # OpenRouter provides OpenAI embeddings at https://openrouter.ai/api/v1/embeddings
    embedding_model: str = Field(
        default="openai/text-embedding-3-small",
        description="OpenRouter embedding model ID"
    )
    embedding_dimension: int = Field(
        default=1536,
        description="Embedding vector dimension"
    )


# Singleton instance
_settings: Settings | None = None


def load_settings() -> Settings:
    """Load settings with proper error handling.

    Returns:
        Settings instance loaded from environment.

    Raises:
        ValueError: If required settings are missing or invalid.
    """
    global _settings
    if _settings is not None:
        return _settings

    try:
        _settings = Settings()
        return _settings
    except Exception as e:
        error_msg = f"Failed to load settings: {e}"
        if "database_url" in str(e).lower():
            error_msg += "\nMake sure to set DATABASE_URL in your .env file"
        if "openrouter_api_key" in str(e).lower():
            error_msg += "\nMake sure to set OPENROUTER_API_KEY in your .env file"
        raise ValueError(error_msg) from e
