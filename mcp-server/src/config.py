"""MCP server configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class ServerSettings(BaseSettings):
    """Configuration for the Athena MCP server.

    All values are loaded from environment variables or a .env file.
    """

    # Obsidian Vault
    vault_path: str = "/vault"

    # Artemis Backend
    artemis_base_url: str = "http://localhost:8000"

    # Elasticsearch
    elastic_url: str = ""
    elastic_api_key: str = ""
    conversations_index: str = "athena-conversations"

    # MCP Server
    mcp_server_port: int = 8001

    # Research (optional)
    tavily_api_key: str = ""
    brave_api_key: str = ""

    # Logging
    log_level: str = "INFO"

    model_config = {
        "env_file": (".env", "../.env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_settings() -> ServerSettings:
    """Create and return settings instance."""
    return ServerSettings()
