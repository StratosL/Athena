# ADR-005: Streamable HTTP Over SSE for MCP Transport

**Date:** 2026-02-13
**Status:** Accepted
**Context:** MCP server needed to connect to Elastic Agent Builder's MCP connector

---

## Problem

The MCP protocol supports two transport modes: SSE (Server-Sent Events) and Streamable HTTP. Our initial implementation used SSE (`mcp.run(transport="sse")`), which is the FastMCP default and the more common option in MCP ecosystem examples. When registering the MCP connector in Elastic Agent Builder, the connection silently failed.

## Discovery

Elastic Agent Builder's MCP connector **only supports Streamable HTTP transport** — not SSE. This is not prominently documented; it was discovered during integration testing on Day 7. Two changes were required:

1. **Transport switch:** `transport="sse"` → `transport="streamable-http"` in FastMCP's `run()` call
2. **Path override:** Elastic's connector POSTs to root `/`, not FastMCP's default `/mcp`. Required setting `streamable_http_path="/"` in the FastMCP constructor.

## Options

| Option | Outcome |
|--------|---------|
| SSE transport (MCP default) | Does not work with Elastic Agent Builder |
| Streamable HTTP with default `/mcp` path | Connector fails — POSTs to `/`, gets 404 |
| Streamable HTTP with `path="/"` | Works correctly |

No real choice here — the platform dictates the transport.

## Decision

Use Streamable HTTP transport mounted at `/`:

```python
mcp = FastMCP(
    "Athena",
    host="0.0.0.0",
    port=settings.mcp_server_port,
    streamable_http_path="/",
)
```

## Consequences

- MCP server works with Elastic Agent Builder
- Streamable HTTP is the newer, recommended MCP transport (spec 2025-03-26+) — future-proof
- Standard HTTP POST semantics means any HTTP-capable tunnel works (ngrok, Cloudflare, etc.)
- SSE-specific tooling (like browser EventSource debugging) no longer applicable
- This also resolved ADR-001's concern about Cloudflare SSE buffering — Streamable HTTP would work fine with Cloudflare Tunnel

## Gotcha for Others

If you're building an MCP server for Elastic Agent Builder:
- Use `transport="streamable-http"`, not `"sse"`
- Set `streamable_http_path="/"` — Elastic's connector POSTs to root
- The connector's URL field is `serverUrl`, not `url`
