"""Indexer configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class IndexerSettings(BaseSettings):
    """Configuration for the Athena indexer.

    All values are loaded from environment variables or a .env file.
    """

    # Elasticsearch
    elastic_url: str
    elastic_api_key: str
    notes_index: str = "athena-notes"
    conversations_index: str = "athena-conversations"

    # Obsidian Vault
    vault_path: str

    # Logging
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


def get_settings() -> IndexerSettings:
    """Create and return settings instance."""
    return IndexerSettings()
