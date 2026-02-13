# ADR-001: Use ngrok for MCP Server Tunneling

**Date:** 2026-02-13
**Status:** Accepted
**Context:** Athena MCP server (SSE transport, port 8001) needs a public URL for Elastic Agent Builder on Elastic Cloud

---

## Problem

Elastic Agent Builder runs on Elastic Cloud and connects to our MCP server via HTTP. During development and demo recording, the MCP server runs locally (or in Docker). We need a tunnel to expose it with a public HTTPS URL.

Requirements:
- SSE (Server-Sent Events) support — MCP protocol uses GET-based SSE for server-to-client streaming and POST for client-to-server messages
- Stable URL preferred — avoids reconfiguring the Elastic MCP connector on every restart
- Free tier sufficient for hackathon use (~14 days, demo recording)
- Reliable during a live demo recording
- Minimal setup time

## Options Evaluated

### ngrok (Selected)

| Aspect | Details |
|--------|---------|
| Free tier | 20K requests/month, 1 GB bandwidth, 3 endpoints |
| Stable URL | Yes — 1 free dev domain (`*.ngrok-free.dev`), persists across restarts |
| SSE support | Full support — both GET and POST SSE work without buffering |
| Session timeout | None — runs indefinitely |
| Setup time | ~2 minutes |
| MCP ecosystem | Official MCP documentation, referenced in Elastic blog posts |

The interstitial browser warning page on the free tier does NOT affect programmatic API calls — only browser HTML requests. Elastic's MCP connector makes HTTP requests and is unaffected.

### Cloudflare Tunnel (cloudflared) — Rejected

| Aspect | Details |
|--------|---------|
| Free tier | Unlimited bandwidth and requests |
| Quick Tunnel SSE | **Broken** — GET-based SSE is buffered until connection closes ([issue #1449](https://github.com/cloudflare/cloudflared/issues/1449)) |
| Named Tunnel SSE | Mostly works, but community reports of buffering up to ~100KB ([issue #199](https://github.com/cloudflare/cloudflared/issues/199)) |
| Setup (Quick) | 1 minute, but SSE is broken |
| Setup (Named) | 15-30 minutes, requires own domain on Cloudflare DNS + Zero Trust config |

**Why rejected:** The MCP SSE transport relies on GET-based Server-Sent Events for server-to-client streaming. Cloudflare Quick Tunnels buffer these entirely, making them non-functional for real-time communication. Named Tunnels mostly work but have residual buffering reports. For a hackathon demo where reliability is critical, this risk is unacceptable.

**Would reconsider if:** We switch to streamable HTTP transport (standard HTTP POST with chunked transfer encoding), which avoids long-lived SSE connections entirely. Cloudflare works perfectly for standard HTTP.

### Tailscale Funnel — Rejected

| Aspect | Details |
|--------|---------|
| Free tier | Included in free Personal plan |
| SSE support | Not confirmed for MCP — likely works (HTTPS proxy) but no community validation |
| Stable URL | Yes (`*.ts.net`) |
| Setup time | 10-15 minutes (install Tailscale, enable Funnel in ACLs) |
| Port restriction | Only exposes on HTTPS 443 — must map to local 8001 |

**Why rejected:** No confirmed SSE/MCP compatibility. More setup overhead than ngrok. Funnel is still in beta. For a hackathon, unverified infrastructure is a risk.

### localtunnel — Rejected

**Why rejected:** Effectively unmaintained. Multi-day outages reported (November 2025). No stable URLs. Too unreliable for a deadline-driven project.

### bore.pub — Rejected

**Why rejected:** TCP-only — no HTTPS. Elastic Agent Builder requires an HTTPS endpoint. Random port assignment on every connection. Not viable.

## Decision

**Use ngrok** with a free static dev domain.

Setup:
```bash
ngrok http --url=athena-mcp.ngrok-free.dev 8001
```

Configure in Elastic Agent Builder MCP connector:
```
https://athena-mcp.ngrok-free.dev/sse
```

Optional Docker Compose integration:
```yaml
ngrok:
  image: ngrok/ngrok:latest
  command: http mcp-server:8001 --url=athena-mcp.ngrok-free.dev
  environment:
    - NGROK_AUTHTOKEN=${NGROK_AUTHTOKEN}
  ports:
    - "4040:4040"
  depends_on:
    - mcp-server
```

## Consequences

- Tunnel URL is stable across restarts — MCP connector configured once
- Free tier limits (20K requests, 1GB) are more than sufficient for hackathon scope
- No SSE buffering issues — MCP protocol works correctly
- Dependency on ngrok's free tier availability (low risk — service has been stable for years)
- If we later switch to streamable HTTP transport, Cloudflare becomes a viable free alternative with no bandwidth limits

## Future Considerations

- **Streamable HTTP transport**: MCP protocol spec (2025-03-26+) recommends streamable HTTP over SSE. FastMCP supports it. Switching would make all tunnel options viable and remove SSE buffering concerns entirely.
- **Production deployment**: For the actual demo recording, consider deploying the MCP server to Railway or Render instead of tunneling — eliminates the tunnel as a failure point.
