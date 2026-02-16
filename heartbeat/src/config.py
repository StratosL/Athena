"""Heartbeat service configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class HeartbeatSettings(BaseSettings):
    """Configuration for the Athena heartbeat service.

    All values are loaded from environment variables or a .env file.
    """

    # Elasticsearch / Kibana
    elastic_url: str = ""
    elastic_api_key: str = ""

    # Agent Builder
    agent_id: str = "athena"

    # Obsidian Vault
    vault_path: str = "/vault"

    # Heartbeat schedule
    heartbeat_interval_minutes: int = 30
    heartbeat_active_hour_start: int = 8  # 8 AM
    heartbeat_active_hour_end: int = 22  # 10 PM

    # Session persistence
    conversation_id_file: str = "/tmp/athena-heartbeat-conversation-id"  # noqa: S108

    # Logging
    log_level: str = "INFO"

    model_config = {
        "env_file": (".env", "../.env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def kibana_url(self) -> str:
        """Derive Kibana URL from Elasticsearch URL."""
        return self.elastic_url.replace(".es.", ".kb.")
