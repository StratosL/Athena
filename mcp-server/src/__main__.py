"""Entry point for `python -m src` — avoids double-import of server module."""

from src.server import logger, mcp, settings

logger.info("Starting Athena MCP server on port %d", settings.mcp_server_port)
mcp.run(transport="streamable-http")
