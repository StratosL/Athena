"""MCP server setup with Streamable HTTP transport.

This is the main entry point for the Athena MCP server.
Initializes adapter classes and registers all tools via FastMCP.
"""

import logging

from mcp.server.fastmcp import FastMCP

from src.config import get_settings

# Initialize settings and logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("elastic_transport").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP(  # noqa: S104
    "Athena",
    host="0.0.0.0",
    port=settings.mcp_server_port,
    streamable_http_path="/",
)

# Initialize adapter classes
from src.artemis_client import ArtemisClient  # noqa: E402
from src.vault_manager import VaultManager  # noqa: E402

vault_manager = VaultManager(settings.vault_path)
artemis_client = ArtemisClient(settings.artemis_base_url)

# ES knowledge store (optional — may not have credentials)
knowledge_store = None
if settings.elastic_url and settings.elastic_api_key:
    from src.es_client import KnowledgeStore

    knowledge_store = KnowledgeStore(
        settings.elastic_url, settings.elastic_api_key, settings.conversations_index
    )

# Research config (for tools/research.py)
tavily_api_key = settings.tavily_api_key
brave_api_key = settings.brave_api_key

# Register all tools (imports trigger @mcp.tool() decorators)
import src.tools.artemis  # noqa: E402
import src.tools.knowledge  # noqa: E402
import src.tools.research  # noqa: E402
import src.tools.vault  # noqa: E402, F401

# Entry point: run via `python -m src` (see __main__.py)
# Do NOT use `python -m src.server` — causes double-import, tools won't register.
