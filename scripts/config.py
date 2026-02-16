"""Shared configuration for setup scripts. Loads from root .env."""

from pydantic_settings import BaseSettings


class SetupConfig(BaseSettings):
    """All environment variables used across setup phases."""

    # Elasticsearch
    elastic_url: str = ""
    elastic_api_key: str = ""

    # Vault / Indexer
    vault_path: str = "./sample-vault"
    notes_index: str = "athena-notes"
    conversations_index: str = "athena-conversations"

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_db_url: str = ""

    # Optional services
    openai_api_key: str = ""
    brave_api_key: str = ""
    tavily_api_key: str = ""

    # ngrok / MCP
    ngrok_domain: str = ""
    mcp_server_port: int = 8001

    @property
    def kibana_url(self) -> str:
        """Derive Kibana URL from Elasticsearch URL."""
        return self.elastic_url.replace(".es.", ".kb.")

    model_config = {"env_file": ("../.env", ".env"), "extra": "ignore"}
